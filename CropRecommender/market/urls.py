from django.urls import path
from . import views

#Registering views created in resource views.py
urlpatterns = [
    path('main/', views.main, name='main'),   
]