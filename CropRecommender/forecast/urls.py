from django.urls import path
from . import views

#Views created in agriBot views.py
urlpatterns = [
    path('forecast/', views.forecast, name='forecast'),
    path('weather/', views.mainSection, name='mainSection'),
    path('locations/', views.get_locations, name='get_locations'),
   
]