
from django.contrib import admin
from django.urls import include, path

# KEYO 11
from django.conf import settings #Allows one to use the MEDIA_URL
from django.conf.urls.static import static
# KEYO 11

# Defining the urls of the apps you have created to contain the logic of different modules
urlpatterns = [
    path('', include('Homepage.urls')), # Homepage module (main) urls are included
    path('', include('agriBot.urls')), #ChatBot module
    path('admin/', admin.site.urls),
    path('social/', include('Social.urls')), #Social media url path
]

if settings.DEBUG: #Development KEYO 11
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
