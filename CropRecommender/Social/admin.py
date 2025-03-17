from django.contrib import admin
from .models import UserProfile, Post, Like, Comment #importing the models created from models.py
# Register your models here.



# Model registration 
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)