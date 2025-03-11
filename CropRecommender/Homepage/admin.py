from django.contrib import admin
from .models import Crop, GAPSection #importing the models created from models.py

# Model registration 
admin.site.register(Crop)
admin.site.register(GAPSection)