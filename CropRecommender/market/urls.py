from django.urls import path
from . import views

#Registering views created in resource views.py main/
urlpatterns = [
    path('', views.main, name='main'),  
    path("edit/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("delete/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("toggle/<int:listing_id>/", views.toggle_availability, name="toggle_availability"),
    #Functions for messages and market place contacting 24/04
    # path("marketplace/", views.marketplace, name="marketplace"),  # Marketplace view
    # path("contact/<int:listing_id>/", views.contactFarmer, name="contactFarmer"),
    # path("conversation/<int:user_id>/", views.conversation, name="conversation"),
]