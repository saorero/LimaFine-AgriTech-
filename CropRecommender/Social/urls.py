# @Keyo Social URLS Configuration
from django.urls import path
from . import views

#Defing the views that exist in Social.Views.py as patterns
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('feed/', views.feed, name='feed'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.likePost, name='likePost'),#likePost view ajax request
    # Add this line for profile_modal
    path('profile_modal/', views.feed, name='profile_modal'),
]
    