
from django.contrib import admin
from django.urls import include, path

# Defining the urls of the apps you have created to contain the logic of different modules
urlpatterns = [
    path('', include('Homepage.urls')), # Homepage module (main) urls are included
    path('', include('agriBot.urls')), #ChatBot module
    path('admin/', admin.site.urls),
    path('social/', include('Social.urls')), #Social media url path
]

