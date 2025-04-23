from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from google.cloud import storage
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_community.document_loaders import GCSFileLoader #helps in reading cloud files
from langchain.text_splitter import RecursiveCharacterTextSplitter #splits text
from langchain_pinecone import PineconeVectorStore #manage vectors
from langchain.prompts import PromptTemplate
from pinecone import Pinecone, ServerlessSpec
import os
import json
import time
from datetime import datetime
from django.utils.timezone import localtime
from dotenv import load_dotenv
from .models import ChatMessage #imports chatHistory model
import uuid

# Load environment variables
load_dotenv()

#  Pinecone client connection for vector Database
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
except Exception as e:
    print(f"Failed to initialize Pinecone: {e}")
    pc = None

# Initialize Gemini model and embeddings(converts text to vectors)
try:
    llm = VertexAI(model_name="gemini-1.5-flash-002", temperature=0.2)
    embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
except Exception as e:
    print(f"Failed to initialize Gemini: {e}")
    llm = None
    embeddings = None

# Path to cache file for tracking indexed files (avoids re-indexing)
CACHE_FILE = r"C:\Users\admin\Downloads\PROJECT\Application\RecommenderSystem\CropRecommender\file_cache.json"

# Load and index documents from new files in the bucket
#process into chunks, convert to embeddings and stores in pinecone
def index_documents():
    try:
        storage_client = storage.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        bucket_name = "smart_farmer"
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix="uploads/")

        # Load cache of previously indexed files
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)

        all_chunks = []
        new_cache = {}
        for blob in blobs:
            if not blob.name.endswith(('.txt', '.pdf')):
                print(f"Skips unsupported files: {blob.name}")
                continue
            # Use updated_time and md5_hash to detect changes
            file_key = blob.name
            updated_time = blob.updated.isoformat()
            md5_hash = blob.md5_hash if blob.md5_hash else ""
            new_cache[file_key] = {"updated_time": updated_time, "md5_hash": md5_hash}

            # Skip if file hasn't changed
            if (file_key in cache and
                cache[file_key]["updated_time"] == updated_time and
                cache[file_key]["md5_hash"] == md5_hash):
                print(f"Skipping unchanged file: {file_key}")
                continue

            try:
                loader = GCSFileLoader(project_name=os.getenv("GOOGLE_CLOUD_PROJECT"), bucket=bucket_name, blob=blob.name)
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(documents)
                all_chunks.extend(chunks)
                print(f"Loaded and split {blob.name}: {len(chunks)} chunks")
            except Exception as e:
                print(f"Failed to load {blob.name}: {e}")

        if all_chunks:
            PineconeVectorStore.from_documents(all_chunks, embeddings, index_name="agri-docs")
            print(f"Indexed {len(all_chunks)} chunks from new/updated files.")
            # Update cache
            with open(CACHE_FILE, 'w') as f:
                json.dump(new_cache, f, indent=2)
        else:
            print("No new or updated documents to index.")
    except Exception as e:
        print(f"Failed to access bucket or index documents: {e}")


# Classification prompt to determine if a query is agriculture-related
classification_prompt_template = """
You are an expert in agriculture. Determine if the following query is related to agriculture, including topics like farming, crops, livestock, soil, irrigation, fertilizers, pest control,agricultural techniques and 
climate/ weather. Answer only 'Yes' or 'No'.

Query: {query}
Answer:
"""
classification_prompt = PromptTemplate(template=classification_prompt_template, input_variables=["query"])

# RAG prompt (agriculture-specific) agriBot
rag_prompt_template = """
You are an agricultural chatbot. Answer the following query based ONLY on the provided context, which contains agriculture-related information. Provide accurate and concise information relevant to agriculture. Do not answer queries outside the scope of agriculture.

Query: {query}
Context: {context}
Answer:
"""
rag_prompt = PromptTemplate(template=rag_prompt_template, input_variables=["query", "context"])

# General knowledge prompt (agriculture-specific)
general_prompt_template = """
You are an agricultural expert chatbot. Answer the following query based on your knowledge of agriculture, including topics like farming, crops, livestock, soil, irrigation, fertilizers, pest control, or agricultural techniques. Provide accurate and concise information. Do not answer queries outside the scope of agriculture.

Query: {query}
Answer:
"""
general_prompt = PromptTemplate(template=general_prompt_template, input_variables=["query"])

@login_required
def chat(request):
    print("Chat endpoint called")
    try:
        vector_store = PineconeVectorStore.from_existing_index(index_name="agri-docs", embedding=embeddings)
        if pc:
            index = pc.Index("agri-docs")
            stats = index.describe_index_stats()
            if stats.get('total_vector_count', 0) == 0:
                print("Indexing documents (empty index)...")
                index_documents()
            else:
                # Check for new files
                print("Checking for new/updated files...")
                storage_client = storage.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
                bucket_name = "smart_farmer"
                bucket = storage_client.bucket(bucket_name)
                blobs = bucket.list_blobs(prefix="uploads/")
                cache = {}
                if os.path.exists(CACHE_FILE):
                    with open(CACHE_FILE, 'r') as f:
                        cache = json.load(f)
                has_new_files = False
                for blob in blobs:
                    file_key = blob.name
                    updated_time = blob.updated.isoformat()
                    md5_hash = blob.md5_hash if blob.md5_hash else ""
                    if (file_key not in cache or
                        cache[file_key]["updated_time"] != updated_time or
                        cache[file_key]["md5_hash"] != md5_hash):
                        has_new_files = True
                        break
                if has_new_files:
                    print("Indexing new/updated documents...")
                    index_documents()
    except Exception as e:
        print(f"Failed to initialize vector store or check index stats: {e}")
        index_documents()  # Fallback
    return render(request, "agriBot.html")

@login_required
def ask_question(request):
    if request.method == "POST":
        query = request.POST.get("query")
        start_time = time.time()
        # For chat history
        conversation_id = request.session.get('conversation_id', str(uuid.uuid4()))
        request.session['conversation_id'] = conversation_id

        # Classify if the query is agriculture-related
        try:
            classification_start = time.time()
            classification_response = llm.invoke(classification_prompt.format(query=query)).strip()
            classification_time = time.time() - classification_start
            if classification_response != "Yes":
                total_time = time.time() - start_time
                print(f"Query: {query}")
                print(f"Classification Time: {classification_time:.2f}s")
                print(f"Total Time: {total_time:.2f}s")
                return JsonResponse({
                    "rag_response": "OOps! I am just a farmer and Agriculture is my business",
                    "general_response": "Hey! I am just a farmer."
                })
        except Exception as e:
            print(f"Failed to classify query: {e}")
            classification_time = 0

        # RAG response (agriculture-specific)
        try:
            rag_start = time.time()
            vector_store = PineconeVectorStore.from_existing_index(index_name="agri-docs", embedding=embeddings)
            retriever = vector_store.as_retriever(search_kwargs={"k": 2})
            relevant_docs = retriever.invoke(query)
            context = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
            rag_retrieval_time = time.time() - rag_start
            if not context:
                rag_response = "No relevant agricultural information found in the documents."
            else:
                llm_start = time.time()
                rag_response = llm.invoke(rag_prompt.format(query=query, context=context))
                llm_rag_time = time.time() - llm_start
        except Exception as e:
            print(f"Failed to retrieve RAG response: {e}")
            rag_response = "No relevant agricultural information found in the documents."
            rag_retrieval_time = 0
            llm_rag_time = 0

        # General knowledge response (agriculture-specific)
        try:
            llm_start = time.time()
            general_response = llm.invoke(general_prompt.format(query=query))
            llm_general_time = time.time() - llm_start
        except Exception as e:
            print(f"Failed to retrieve general response: {e}")
            general_response = "Unable to process the agricultural query at this time."
            llm_general_time = 0
        

         # Save them to ChatMessage database
        ChatMessage.objects.create(
            user=request.user,
            query=query,
            rag_response=rag_response,
            general_response=general_response,
            conversation_id=conversation_id
        )

        total_time = time.time() - start_time
        
        print(f"Query: {query}")
        print(f"Classification Time: {classification_time:.2f}s")
        print(f"RAG Retrieval Time: {rag_retrieval_time:.2f}s")
        print(f"RAG LLM Time: {llm_rag_time:.2f}s")
        print(f"General LLM Time: {llm_general_time:.2f}s")
        print(f"Total Time: {total_time:.2f}s")

        return JsonResponse({
            "rag_response": rag_response,
            "general_response": general_response,
            # chat tracking
            "timestamp": localtime().isoformat(),
            "conversation_id": conversation_id
        })
    return JsonResponse({"error": "Invalid request method"})


# Chat History Views
@login_required
def get_chat_history(request):
    conversations = ChatMessage.objects.filter(user=request.user).values('conversation_id', 'timestamp').distinct()
    history = [
        {
            'conversation_id': conv['conversation_id'],
            'date': conv['timestamp'].strftime('%Y-%m-%d ')
            # %H:%M:%S
        }
        for conv in conversations
    ]
    return JsonResponse({'history': history})

@login_required
def get_conversation(request, conversation_id):
    messages = ChatMessage.objects.filter(user=request.user, conversation_id=conversation_id).order_by('timestamp')
    conversation = [
        {
            'query': msg.query,
            'rag_response': msg.rag_response,
            'general_response': msg.general_response,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    return JsonResponse({'conversation': conversation})



