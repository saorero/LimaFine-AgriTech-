from django.urls import path
from . import views

#Registering views created in resource views.py
urlpatterns = [
    
    path('hub/', views.hub, name='hub'),
    path('videoSection/', views.videoSection, name="videoSection"),
    path('fetchDocuments/', views.fetchDocuments, name='fetchDocuments'),
    path('articles/', views.articleSection, name='articleSection'),#added now

   
]