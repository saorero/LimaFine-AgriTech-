from django.urls import path
from . import views

#Registering views created in resource views.py main/
urlpatterns = [
    path('', views.main, name='main'),  
    path("edit/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("delete/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("toggle/<int:listing_id>/", views.toggle_availability, name="toggle_availability"),
    
 
]