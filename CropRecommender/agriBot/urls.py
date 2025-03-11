from django.urls import path
from . import views

#Views created in agriBot views.py
urlpatterns = [
    path('agriBot/', views.agriBot, name='agriBot'),
   
]