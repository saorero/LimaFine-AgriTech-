from django.urls import path
from . import views

#Registering views created in resource views.py main/
urlpatterns = [
    path('', views.main, name='main'),  
    path("edit/<int:listing_id>/", views.editListing, name="editListing"),
    path("delete/<int:listing_id>/", views.deleteListing, name="deleteListing"),
    path("toggle/<int:listing_id>/", views.toggle_availability, name="toggle_availability"),
    # 25/04 MESSAGES
    path('messages/send/', views.sendMessage, name='sendMessage'),
    path('messages/conversations/', views.getConversations, name='getConversations'),
    # path('messages/<int:listing_id>/<int:other_user_id>/', views.getMessages, name='getMessages'),
    path('messages/<str:listing_id>/<int:other_user_id>/', views.getMessages, name='getMessages'),  # Changed to str to allow 'none'
 

    # REQUEST
    path('request/create/', views.create_product_request, name='create_product_request'), #to create product request
    path('request/edit/<int:request_id>/', views.edit_product_request, name='edit_product_request'),
    path('request/delete/<int:request_id>/', views.delete_product_request, name='delete_product_request'),
    path('my_requests/', views.get_my_requests, name='get_my_requests'), #filters out result of productRequests
    path('product_requests/', views.get_product_requests, name='get_product_requests'), #// Loads all product requests

    # ORDER PATHS
    path('createOrder/', views.createOrder, name='createOrder'),
    path('farmerOrders/', views.getFarmerOrders, name='getFarmerOrders'),
    path('updateOrderStatus/<int:order_id>/', views.updateOrderStatus, name='updateOrderStatus'),
    path('myOrders/', views.getMyOrders, name='getMyOrders'),
    path('deleteOrder/<int:order_id>/', views.deleteOrder, name='deleteOrder'),


    path('optimize_delivery_route/', views.optimize_delivery_route, name='optimize_delivery_route'),
    path('update_farmer_location/', views.update_farmer_location, name='update_farmer_location'),
]