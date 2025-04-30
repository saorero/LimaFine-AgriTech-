# This file is important since it holds the google API key that was used for integrating the location selection logic
# It loads the api defined in seetings.py
# Allows reusability since market.html might have been rendered in other templates
from django.conf import settings

def google_maps_api_key(request):
    return {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }