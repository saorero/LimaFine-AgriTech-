from django.urls import path
from . import views

#Registering views created in resource views.py main/
urlpatterns = [
    path('', views.main, name='main'),  
    path("edit/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("delete/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("toggle/<int:listing_id>/", views.toggle_availability, name="toggle_availability"),
    # 25/04
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/conversations/', views.get_conversations, name='get_conversations'),
    path('messages/<int:listing_id>/<int:other_user_id>/', views.get_messages, name='get_messages'),
 
]