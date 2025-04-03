# CREATED to handle content checking function So this is where the trained model
# I had created contentFiltrationModel is loaded and used
import os

# April 3rd
# Content Validation imports
from django.core.exceptions import ValidationError
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# FineTuned Model Load
model_path = os.path.join(os.getcwd(), 'contentFiltrationModel')
tokenizer = DistilBertTokenizer.from_pretrained(model_path, local_files_only=True)
model = DistilBertForSequenceClassification.from_pretrained(model_path)
model.eval()  # Set model to evaluation mode

# Check content posted in the different models
def checkContent(text):
    """Check if text is agricultural using AI model"""
    print("Checking content...")
    inputs = tokenizer(text, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = torch.argmax(probabilities, dim=1).item()
    
    return predicted_class == 1  # Return True if Agricultural, False otherwise

# April 3rd