
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import pandas as pd
import joblib
import pickle
from datetime import datetime, timedelta
import numpy as np
from sklearn.preprocessing import LabelEncoder
from .models import Crop #import models for this app
import os
from dotenv import load_dotenv#loads env file for defined APIs
from django.core.cache import cache #caches the result received from GAPs
import google.generativeai as genai #for gemini model
import re
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


load_dotenv()
# Load pre-trained models and encoders
cropModel = joblib.load("Homepage/modelsMe/model_2.joblib")#model for crop prediction
label_encoder = joblib.load("Homepage/modelsMe/encoder2.joblib")#crop prediction

# Weather models loaded
with open('Homepage/modelsMe/weatherScaler.pkl', 'rb') as f:
    weatherScaler = pickle.load(f)
# with open('Homepage/modelsMe/rainModel.pkl', 'rb') as f:
#     rainModel = pickle.load(f)
# with open('Homepage/modelsMe/tempModel.pkl', 'rb') as f:
#     tempModel = pickle.load(f)
# with open('Homepage/modelsMe/humidityModel.pkl', 'rb') as f:
#     humidityModel = pickle.load(f)
rainModel = XGBRegressor()
rainModel.load_model(os.path.join(BASE_DIR, 'Homepage', 'modelsMe', 'rainModel.json'))
tempModel = XGBRegressor()
tempModel.load_model(os.path.join(BASE_DIR, 'Homepage', 'modelsMe', 'tempModel.json'))
humidityModel = XGBRegressor()
humidityModel.load_model(os.path.join(BASE_DIR, 'Homepage', 'modelsMe', 'humidityModel.json'))

# Backup coordinates file
locationData = pd.read_excel("static/data/countyCoordinates.xlsx")

# Dictionary to hold crop images
cropImages = {
    "Beans": "beans.jpg",
    "rice": "rice.jpg",
    "Cashewnuts": "cashewnut.jpg",
    "Onion": "onion.jpg",
    "Banana": "banana.jpg",
    "Cabbage": "cabbage.jpg",
    "papaya": "papaya.jpg",
    

}


# Historical weather data is processed to get previous weather values

def processData(file_path=os.path.join(BASE_DIR, 'Homepage', 'daily.csv')):
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Aggregate to monthly data
    monthly_data = df.groupby(['year', 'month', 'latitude', 'longitude']).agg({
        'rainfall': 'sum',
        'temperature': 'mean',
        'humidity': 'mean'
    }).reset_index()
    
    # Sort by date and location
    monthly_data = monthly_data.sort_values(['latitude', 'longitude', 'year', 'month'])
    
    # Add lagged features
    for var in ['rainfall', 'temperature', 'humidity']:
        monthly_data[f'prev_{var}'] = monthly_data.groupby(['latitude', 'longitude'])[var].shift(1)
        monthly_data[f'prev2_{var}'] = monthly_data.groupby(['latitude', 'longitude'])[var].shift(2)
    
    # Add moving averages
    for var in ['rainfall', 'temperature', 'humidity']:
        monthly_data[f'ma6_{var}'] = monthly_data.groupby(['latitude', 'longitude'])[var].rolling(window=6, min_periods=1).mean().reset_index(level=[0,1], drop=True)
        monthly_data[f'ma12_{var}'] = monthly_data.groupby(['latitude', 'longitude'])[var].rolling(window=12, min_periods=1).mean().reset_index(level=[0,1], drop=True)
    
    # Cyclical encoding for month
    monthly_data['month_sin'] = np.sin(2 * np.pi * monthly_data['month'] / 12)
    monthly_data['month_cos'] = np.cos(2 * np.pi * monthly_data['month'] / 12)
    
    # Drop rows with NaN values
    monthly_data = monthly_data.dropna()
    
    return monthly_data

def weatherPrediction(latitude, longitude): 
    
    # Define feature names expected by the models
    featureNames = ['month_sin', 'month_cos', 'latitude', 'longitude',
                    'prev_rainfall', 'prev_temperature', 'prev_humidity',
                    'prev2_rainfall', 'prev2_temperature', 'prev2_humidity',
                    'ma6_rainfall', 'ma6_temperature', 'ma6_humidity',
                    'ma12_rainfall', 'ma12_temperature', 'ma12_humidity']
    
    # Get current date and move to the first of next month
    currentDate = datetime.now()
    print(f"Current Date: {currentDate}")
    nextMonth = currentDate.replace(day=1) + timedelta(days=32)
    startDate = nextMonth.replace(day=1)
    
    predictions = {'month': [], 'rainfall': [], 'temperature': [], 'humidity': []}
    
    # Load historical data for initial lagged and moving average features
    monthly_data = processData()
    location_data = monthly_data[(monthly_data['latitude'] == latitude) & (monthly_data['longitude'] == longitude)]
    
    if not location_data.empty:
        recent_data = location_data.tail(2)  # Last two months for prev and prev2
        prev_rainfall = recent_data['rainfall'].iloc[-1]
        prev_temperature = recent_data['temperature'].iloc[-1]
        prev_humidity = recent_data['humidity'].iloc[-1]
        prev2_rainfall = recent_data['rainfall'].iloc[-2] if len(recent_data) > 1 else prev_rainfall
        prev2_temperature = recent_data['temperature'].iloc[-2] if len(recent_data) > 1 else prev_temperature
        prev2_humidity = recent_data['humidity'].iloc[-2] if len(recent_data) > 1 else prev_humidity
        ma6_rainfall = recent_data['ma6_rainfall'].iloc[-1]
        ma6_temperature = recent_data['ma6_temperature'].iloc[-1]
        ma6_humidity = recent_data['ma6_humidity'].iloc[-1]
        ma12_rainfall = recent_data['ma12_rainfall'].iloc[-1]
        ma12_temperature = recent_data['ma12_temperature'].iloc[-1]
        ma12_humidity = recent_data['ma12_humidity'].iloc[-1]
    else:
        # Fallback: use global averages
        prev_rainfall = monthly_data['rainfall'].mean()
        prev_temperature = monthly_data['temperature'].mean()
        prev_humidity = monthly_data['humidity'].mean()
        prev2_rainfall = prev_rainfall
        prev2_temperature = prev_temperature
        prev2_humidity = prev_humidity
        ma6_rainfall = monthly_data['rainfall'].mean()
        ma6_temperature = monthly_data['temperature'].mean()
        ma6_humidity = monthly_data['humidity'].mean()
        ma12_rainfall = monthly_data['rainfall'].mean()
        ma12_temperature = monthly_data['temperature'].mean()
        ma12_humidity = monthly_data['humidity'].mean()
    
    current_pred_date = startDate
    
    for i in range(12):
        month = current_pred_date.month
        # Cyclical encoding for month
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        
        # Prepare features
        features = pd.DataFrame([[month_sin, month_cos, latitude, longitude,
                                 prev_rainfall, prev_temperature, prev_humidity,
                                 prev2_rainfall, prev2_temperature, prev2_humidity,
                                 ma6_rainfall, ma6_temperature, ma6_humidity,
                                 ma12_rainfall, ma12_temperature, ma12_humidity]],
                               columns=featureNames)
        featureScale = weatherScaler.transform(features)
        
        # Predict weather conditions
        rainPrediction = rainModel.predict(featureScale)[0]
        tempPrediction = tempModel.predict(featureScale)[0]
        humidityPrediction = humidityModel.predict(featureScale)[0]
        
        # Ensure realistic values
        rainPrediction = max(0, rainPrediction)
        humidityPrediction = max(0, min(100, humidityPrediction))
        
        # Store predictions
        predictions['month'].append(current_pred_date.strftime('%B %Y'))
        predictions['rainfall'].append(rainPrediction)
        predictions['temperature'].append(tempPrediction)
        predictions['humidity'].append(humidityPrediction)
        
        # Update lagged and moving average features
        prev2_rainfall = prev_rainfall
        prev2_temperature = prev_temperature
        prev2_humidity = prev_humidity
        prev_rainfall = rainPrediction
        prev_temperature = tempPrediction
        prev_humidity = humidityPrediction
        # Approximate moving averages
        ma6_rainfall = (ma6_rainfall * 5 + rainPrediction) / 6
        ma6_temperature = (ma6_temperature * 5 + tempPrediction) / 6
        ma6_humidity = (ma6_humidity * 5 + humidityPrediction) / 6
        ma12_rainfall = (ma12_rainfall * 11 + rainPrediction) / 12
        ma12_temperature = (ma12_temperature * 11 + tempPrediction) / 12
        ma12_humidity = (ma12_humidity * 11 + humidityPrediction) / 12
        
        # Move to next month
        nextMonth = current_pred_date.month % 12 + 1
        nextYear = current_pred_date.year + (current_pred_date.month // 12)
        current_pred_date = current_pred_date.replace(year=nextYear, month=nextMonth, day=1)
    
    totalRain = sum(predictions['rainfall'])
    avgTemp = sum(predictions['temperature']) / 12
    avgHumidity = sum(predictions['humidity']) / 12
    
    print("\nSummary for the Next 12 Months:")
    print(f"Total Rainfall: {totalRain:.2f} mm")
    print(f"Average Temperature: {avgTemp:.2f} °C")
    print(f"Average Humidity: {avgHumidity:.2f} %")
    
    return totalRain, avgTemp, avgHumidity


# Soil Data Fetching
def soilData(lat, lon): 
    soilAPI = os.getenv('SoilAPI')
    # soilAPI = os.getenv('FakeAPI')
    url = f"https://api.isda-africa.com/v1/soilproperty?key={soilAPI}&lat={lat}&lon={lon}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to get data: {response.status_code}")
        data = response.json()
        
        properties = ['ph', 'sand_content', 'clay_content']
        soilInfo = {}
        
        for prop in properties:
            if prop in data['property']:
                value = data['property'][prop][0]['value']['value']
                if prop in ['sand_content', 'clay_content']:
                    soilInfo[prop] = value * 10
                else:
                    soilInfo[prop] = value
            else:
                soilInfo[prop] = 0

        # debugging prints
        print("Using fetched soil values from iSDA")
        print(f"soilInfo: {soilInfo}") #to delete displays the soilInfo collected
        
        return soilInfo
    except Exception as e: #Default Values if API fails
        print(f"Soil API error: {e}\n Using Default soil Vaues")
        
        return {"ph": 0, "sand_content": 0, "clay_content": 0}

# Fetch GAPs from Gemini
def fetch_gaps_from_gemini(crop):
    cache_key = f"gap_{crop.lower()}"
    cached_gaps = cache.get(cache_key)
    if cached_gaps:
        return cached_gaps

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-002')
     
        prompt = f"""
        Provide detailed Good Agricultural Practices (GAPs) for growing {crop} in Kenya, focusing on reputable sources such as KALRO, FAO Kenya,kalrotimps, and other Kenyan agricultural institutions. Structure the response with clear section headings and provide detailed content under each section. Ensure the information is specific to the Kenyan context.
        """
        response = model.generate_content(prompt)
        if not response.text:
            raise Exception("Empty response from Gemini API")

        # Parse response to extract sections and content
        gaps = {}
        lines = response.text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # Detect section headings (e.g., ## Section Name)
            if line.startswith('## '):
                if current_section:
                    gaps[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = line[3:].strip()
            elif current_section:
                current_content.append(line)

        if current_section and current_content:
            gaps[current_section] = '\n'.join(current_content).strip()

        # Cache the result for 24 hours
        cache.set(cache_key, gaps, timeout=24*60*60)
        return gaps
    except Exception as e:
        print(f"Gemini API error for {crop}: {e}")
        return {}

# Crop Prediction Function
# cropPrediction also calls the other two functions(weatherPrediction & soilData) , the result from this place is sent back to
# predict function
def cropPrediction(lat, lon):
    totalRain, avgTemp, avgHumidity = weatherPrediction(lat, lon)
    soilProperties = soilData(lat, lon)
    # Data to be passed to the cropModel
    newData = pd.DataFrame({
        "Rainfall": [totalRain],
        "Temperature": [avgTemp],
        "Humidity": [avgHumidity],
        "pH": [soilProperties['ph']],
        "Sand": [soilProperties['sand_content']],
        "Clay": [soilProperties['clay_content']]
    })
    
    prediction = cropModel.predict_proba(newData)#feeds the user input Data
    indexValues = np.argsort(prediction[0])[::-1][:3]
    topCrops = label_encoder.inverse_transform(indexValues)
    cropsPredicted = prediction[0][indexValues] * 100
    
    results = []
    for crop, conf in zip(topCrops, cropsPredicted):
        # Resorts to default if the crop image does not exist
        imageFile = cropImages.get(crop, "default.jpg")
        imagePath = f"/static/Images/crops/{imageFile}"
         # Ensure crop exists in DB, creates an instance of the crop if it does not exist
        crop_obj, _ = Crop.objects.get_or_create(
            name=crop,
            defaults={"image": imageFile}
        )
        
        # Fetch GAPs from Gemini
        gap_data = fetch_gaps_from_gemini(crop)
        # appends the results with the GAPs to that have bbenfetched
        # The results are used in frontend with predict function acting as a bridge between cropPredict and frontend
        results.append({
            "crop": crop,
            "confidence": float(conf),
            "image": imagePath,
            "gap": gap_data
        })
    return results

@csrf_exempt
def predict(request):
    if request.method == "POST":#once you presss the predict button
        try:
            data = json.loads(request.body)
            # Check for geolocation input (lat, lng)
            if "lat" in data and "lng" in data:
                try:
                    lat = float(data["lat"])
                    lng = float(data["lng"])
                    # Validate latitude and longitude ranges
                    if not (-90 <= lat <= 90):
                        return JsonResponse({"error": "Invalid latitude value"}, status=400)
                    if not (-180 <= lng <= 180):
                        return JsonResponse({"error": "Invalid longitude value"}, status=400)
                    coordinates = {"lat": lat, "lng": lng}
                except (ValueError, TypeError):
                    return JsonResponse({"error": "Latitude and longitude must be valid numbers"}, status=400)
            # Check for manual input (constituency, ward)
            elif "constituency" in data and "ward" in data:
                constituency = data.get("constituency", "").strip().lower()
                ward = data.get("ward", "").strip().lower()
                
                # If constituency and wards are missing (All should be filled)
                if not (constituency and ward):
                    return JsonResponse({"error": "Fill all fields"}, status=400)
                
                locationQuery = f"{ward}, {constituency}, Kenya"
                
                 # Geolocation APIs defined
                apiKeys = [
                    os.getenv("locationAPI1"), #These are correct APIs uncomment them to work as expected
                    os.getenv("locationAPI2"),
                    # os.getenv("FakeAPI")  # Replace with real APIs as needed
                ]
                
                # Fetches location co-ordinates from the names that have been passed ward and cosnstituency
                def fetchCoordinates(apiKey):
                    try:
                        apiUrl = "https://api.opencagedata.com/geocode/v1/json"
                        params = {"q": locationQuery, "key": apiKey, "limit": 1}
                        response = requests.get(apiUrl, params=params)
                        responseData = response.json()
                        if responseData.get("results"):
                            return responseData["results"][0]["geometry"]
                    except Exception as e:
                        print(f"OpenCage API error with key {apiKey}: {e}")
                    return None  #do not return anything if it fails
                
                coordinates = None
                for apiKey in apiKeys:#for every API key defined try all of them
                    coordinates = fetchCoordinates(apiKey)#calls the function to get the coOrdinates passing in the keys
                    if coordinates:#continue if coordinates found and proceed to call cropsPrediction
                        print("Yayy location coordinates found")#Debug line
                        break
                
                if not coordinates:#if not found in API resort to Excel Backup file
                    print("All API keys failed, resorting to Excel backup.")
                    locationData["constituency_name"] = locationData["constituency_name"].str.strip().str.lower()
                    locationData["constituencies_wards"] = locationData["constituencies_wards"].str.strip().str.lower()
                    backupData = locationData[
                        (locationData["constituency_name"] == constituency) &
                        (locationData["constituencies_wards"] == ward)
                    ]
                    if not backupData.empty:
                        latitude = backupData.iloc[0]["Latitude"]
                        longitude = backupData.iloc[0]["Longitude"]
                        coordinates = {"lat": latitude, "lng": longitude}
                    else:
                        return JsonResponse({"error": "Location not specified in backup"}, status=404)
            else:
                return JsonResponse({"error": "Provide either latitude/longitude or constituency/ward"}, status=400)
            
            # Call cropPrediction with coordinates found and stores the predictions in crop_results
            crop_results = cropPrediction(coordinates["lat"], coordinates["lng"])
            # Returns this result to frontend that is coordinates and crop_results gotten from cropPrediction function that was called
            return JsonResponse({
                "coordinates": coordinates,
                "crop_predictions": crop_results#results from cropPrediction function
            })
        
        except Exception as e:#when an error occurs 
            print(f"Error has occurred: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method try POST"}, status=400)

# Location dropdown functions (unchanged)
def countyLoad(request):
    with open('static/data/locationData.json') as file:
        data = json.load(file)
    counties = [{"id": county["county_code"], "name": county["county_name"]} for county in data]
    return JsonResponse({"counties": counties}) #returns only the countyName

def subcountyLoad(request):
    county_code = int(request.GET.get('county_code'))
    with open('static/data/locationData.json') as file:
        data = json.load(file)
    for county in data:
        if county["county_code"] == county_code:
            constituencies = [{"name": constituency["constituency_name"]} for constituency in county["constituencies"]]
            return JsonResponse({"constituencies": constituencies})
    return JsonResponse({"constituencies": []})

def wardLoad(request):
    county_code = int(request.GET.get('county_code'))
    constituency_name = request.GET.get('constituency_name')
    with open('static/data/locationData.json') as file:
        data = json.load(file)
    for county in data:
        if county["county_code"] == county_code:
            for constituency in county["constituencies"]:
                if constituency["constituency_name"] == constituency_name:
                    wards = [{"name": ward} for ward in constituency["wards"]]
                    return JsonResponse({"wards": wards})
    return JsonResponse({"wards": []})

def Homepage(request):
    return render(request, 'Homepage.html')