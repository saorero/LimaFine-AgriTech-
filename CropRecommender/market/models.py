from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from Social.models import UserProfile
from storages.backends.gcloud import GoogleCloudStorage

from .utils import checkContent

# # April 3rd
# # Content Validation imports
# from django.core.exceptions import ValidationError
# from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
# import torch

# # FineTuned Model Load
# model_path = os.path.join(os.getcwd(), 'contentFiltrationModel')
# tokenizer = DistilBertTokenizer.from_pretrained(model_path, local_files_only=True)
# model = DistilBertForSequenceClassification.from_pretrained(model_path)
# model.eval()  # Set model to evaluation mode

# # Check content posted in the different models
# def checkContent(text):
#     """Check if text is agricultural using AI model"""
#     print("Checking content...")
#     inputs = tokenizer(text, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
    
#     with torch.no_grad():
#         outputs = model(**inputs)

#     probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
#     predicted_class = torch.argmax(probabilities, dim=1).item()
    
#     return predicted_class == 1  # Return True if Agricultural, False otherwise

# # April 3rd


# Create your models here.
# Table that store the requests made by users 
class ProductRequest(models.Model):
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='product_requests')
    product_name = models.CharField(max_length=100, blank=False)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default="kg")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} requested by {self.requester.user.username}"
    
    # FOR VALIDATING CONTENT ENTERED
    def clean(self):
        """Override the clean method to validate content relevance before saving"""
        if not checkContent(self.product_name):
            raise ValidationError({'product_name': 'Product name is not related to agriculture. Please edit.'})

        if not checkContent(self.description):
            raise ValidationError({'description': 'Description is not agriculturally relevant. Please edit.'})

    def save(self, *args, **kwargs):
        """Override the save method to ensure validation before saving"""
        self.clean()  # Ensure clean() is called before saving
        super().save(*args, **kwargs)  # Call the parent class's save method

# For farmers product productproductListing
class productListing(models.Model):
    farmer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'})
    # product Category choices
    productCategoryChoices = (
        ('crop', 'Crop'),
        ('dairy', 'Dairy product'),
        ('meat', 'Meat product'),
    )
    productCategory = models.CharField(max_length=20, choices=productCategoryChoices, default='crop')    
    productName = models.CharField(max_length=100, blank=False)    
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default="kg")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='productListingsImages/', blank=True, null=True, storage=GoogleCloudStorage())

    
    # If location is not defined choose the deafult user loccation from farmers profile
    def save(self, *args, **kwargs):
        if not self.location:
            self.location = self.farmer.county
        super().save(*args, **kwargs)

    def get_image_url(self):
        # if image is uploaded fetch the image url 
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            # if image not uploaded then use the ones available in static
            product_image_name = self.productName.lower() + ".jpg"
            static_image_path = f"Images/crops/{product_image_name}"
            static_root = os.path.join(settings.STATICFILES_DIRS[0], static_image_path)
            if os.path.exists(static_root):
            
                return f"/static/Images/crops/{product_image_name}"
            return "/static/Images/crops/default.jpg"

    def __str__(self):#easy identification in admin tomatoes by akeyo
        return f"{self.productName} by {self.farmer.user.username}"



class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
    listing = models.ForeignKey(productListing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.recipient.user.username}"

