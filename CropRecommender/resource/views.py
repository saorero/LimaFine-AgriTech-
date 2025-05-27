import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import random

# For handling Google Cloud Storage files
from google.cloud import storage
from django.conf import settings

import os
from dotenv import load_dotenv
load_dotenv()

# Create your views here.
# Views for Resource application

# VIEWS TO HANDLE VIDEOS
def fetchVideos(query="agriculture", maxResults=12):
    

    # youtubeApi = os.getenv("youtubeApiWrong")
    youtubeApi = os.getenv("youtubeApi")
    youtubeSearch = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": maxResults,
        "key": youtubeApi,
    }
    response = requests.get(youtubeSearch, params=params)  # Request sent to YouTube
    
    if response.status_code == 200:
        videos = response.json().get("items", [])
        return [
            {
                "title": video["snippet"]["title"],
                "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"],
                "video_id": video["id"]["videoId"],
            }
            for video in videos
        ]
    else:
        # To handle API fail      
        return {"error": "An unknown error occurred while fetching videos."}

# Function to handle video requests
def videoSection(request):
    query = request.GET.get("q", None)  # Search items defined by user
    if query is None:  # If not defined by user, pick searches at random
        query = random.choice(["agriculture", "farming", "crops", "soil health", "organic farming", "agriculture kenya"])
    videos = fetchVideos(query)  # Fetch related video content
    return render(request, "resource.html", {"videos": videos, "section": "videos"})

# VIEWS TO HANDLE ARTICLES FROM GOOGLE CLOUD STORAGE
def fetchDocuments(request):
    """Fetch non-image files from Google Cloud Storage and return as JSON."""
    client = storage.Client()
    bucket = client.bucket(settings.GS_BUCKET_NAME)
    blobs = bucket.list_blobs()

    files = [
        {
            # "name": blob.name,
            "name": os.path.basename(blob.name),  # extracts only filename
            "url": blob.public_url,
            "extension": blob.name.split('.')[-1]
        }
        for blob in blobs if not blob.name.endswith(('.jpg', '.png'))  # Exclude images
    ]

    return JsonResponse({"files": files})

def articleSection(request):
    """Render the articles section."""
    return render(request, "resource.html", {"section": "articles"})

def hub(request):
    """Render the hub landing page."""
    context = {'message': 'Welcome to Agri Hub Resource Galore!', "section": "hub"}
    return render(request, 'resource.html', context)