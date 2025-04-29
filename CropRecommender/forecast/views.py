from django.shortcuts import render
from django.http import HttpResponse
# mine
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json
from django.conf import settings
import os

from dotenv import load_dotenv
load_dotenv()

def get_locations(request):
    # Path to your JSON file in static/data
    json_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'locationData.json')
    with open(json_path, 'r') as file:
        locations = json.load(file)
    return JsonResponse(locations, safe=False)


@require_GET
def forecast(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    ward = request.GET.get('ward')  # New parameter for ward selection
    api_key = os.getenv("forecastApi")

    if ward:
        # Use OpenWeatherMap Geocoding API to get coordinates from ward name
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={ward},KE&limit=1&appid={api_key}"
        geo_response = requests.get(geocoding_url)
        if geo_response.status_code == 200 and geo_response.json():
            geo_data = geo_response.json()[0]
            lat = geo_data['lat']
            lon = geo_data['lon']
        else:
            return JsonResponse({'error': 'Unable to find coordinates for the selected location'}, status=400)

    if not lat or not lon:
        return JsonResponse({'error': 'Location coordinates are required'}, status=400)

    # Fetch 5-day forecast from OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        forecast = []
        for entry in data['list'][::8]:  # One entry per day
            day_forecast = {
                'date': entry['dt_txt'],
                'temp': entry['main']['temp'],
                'weather': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon']
            }
            forecast.append(day_forecast)
        return JsonResponse({'forecast': forecast[:5]})
    else:
        return JsonResponse({'error': 'Unable to fetch weather data'}, status=500)

def mainSection(request):
    return render(request, 'forecast.html')
