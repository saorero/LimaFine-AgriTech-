from django.contrib import admin
from .models import Crop #importing the models created from models.py , GAPSection

# Model registration 
admin.site.register(Crop)
# admin.site.register(GAPSection)