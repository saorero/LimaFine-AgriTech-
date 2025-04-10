from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from Social.models import UserProfile
from storages.backends.gcloud import GoogleCloudStorage

from .utils import checkContent #content validation function

# Create your models here.
# Table for the orders made for a productListing 08
class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    )
    
    listing = models.ForeignKey('productListing', on_delete=models.CASCADE, related_name='orders')
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_made')
    quantity = models.FloatField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def clean(self):
        """Validate order details."""
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than 0.'})
        if self.quantity > self.listing.quantity:
            raise ValidationError({'quantity': f'Quantity requested ({self.quantity}) exceeds available ({self.listing.quantity}).'})
        if self.total_price != (self.quantity * float(self.listing.price)):
            raise ValidationError({'total_price': 'Total price does not match quantity × listing price.'})

    def save(self, *args, **kwargs):
        """Override save to calculate total_price and reduce listing quantity."""
        if not self.pk:  # Only on creation
            self.total_price = self.quantity * float(self.listing.price)
            self.listing.quantity -= self.quantity
            if self.listing.quantity <= 0:
                self.listing.is_available = False
            self.listing.save()
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} for {self.listing.productName} by {self.requester.user.username}"

# 08

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
    
    # FOR VALIDATING CONTENT ENTERED Commented out for now
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

