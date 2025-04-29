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
from .models import Crop, GAPSection  # Import your models
import os
from dotenv import load_dotenv #loads env file for defined APIs

load_dotenv()
# Load pre-trained models and encoders
cropModel = joblib.load("Homepage/modelsMe/model_2.joblib")
label_encoder = joblib.load("Homepage/modelsMe/encoder2.joblib")
with open('Homepage/modelsMe/weatherScaler.pkl', 'rb') as f:
    weatherScaler = pickle.load(f)
with open('Homepage/modelsMe/rainModel.pkl', 'rb') as f:
    rainModel = pickle.load(f)
with open('Homepage/modelsMe/tempModel.pkl', 'rb') as f:
    tempModel = pickle.load(f)
with open('Homepage/modelsMe/humidityModel.pkl', 'rb') as f:
    humidityModel = pickle.load(f)

# Backup coordinates file
locationData = pd.read_excel("static/data/countyCoordinates.xlsx")

# Dictionary to hold crop images
cropImages = {
    "Beans": "beans.jpg",
    "rice": "rice.jpg",
    "Cashewnuts": "cashewnut.jpg",
    "Onion": "onion.jpg"
}

# Weather Prediction Function  //RANDOM forest
def weatherPrediction(latitude, longitude):
    featureNames = ['month', 'latitude', 'longitude']
    currentDate = datetime.now()
    print(f"Current Date: {currentDate}")
    nextMonth = currentDate.replace(day=1) + timedelta(days=32)
    startDate = nextMonth.replace(day=1)
    
    predictions = {'rainfall': [], 'temperature': [], 'humidity': []}
    current_pred_date = startDate
    
    for i in range(12):
        month = current_pred_date.month
        features = pd.DataFrame([[month, latitude, longitude]], columns=featureNames)
        featureScale = weatherScaler.transform(features) #scales the features
        
        # prediction of weather conditions takes place via model loading
        rainPrediction = rainModel.predict(featureScale)[0]
        tempPrediction = tempModel.predict(featureScale)[0]
        humidityPrediction = humidityModel.predict(featureScale)[0]
        
        predictions['rainfall'].append(max(0, rainPrediction))
        predictions['temperature'].append(tempPrediction)
        predictions['humidity'].append(max(0, min(100, humidityPrediction)))
        
        nextMonth = current_pred_date.month % 12 + 1
        nextYear = current_pred_date.year + (current_pred_date.month // 12)
        current_pred_date = current_pred_date.replace(year=nextYear, month=nextMonth, day=1)

    totalRain = sum(predictions['rainfall'])
    avgTemp = sum(predictions['temperature']) / 12
    avgHumidity = sum(predictions['humidity']) / 12
    print(f"Weather Values {totalRain},{avgTemp},{avgHumidity}")
    return totalRain, avgTemp, avgHumidity

# Soil Data Fetching
def soilData(lat, lon): 
    soilAPI = os.getenv('FakeAPI')
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
        print(f"soilInfo: {soilInfo}") #to delete displays the soilInfo collected
        
        return soilInfo
    except Exception as e: #Default Values if API fails
        print(f"Soil API error: {e}\n Using Default soil Vaues")
        
        return {"ph": 0, "sand_content": 0, "clay_content": 0}

# Crop Prediction Function with Database GAP LOGIC
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
    
    prediction = cropModel.predict_proba(newData) #feeds the user input Data
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
        # Fetch GAP sections from database
        gap_data = {section.section_name: section.description for section in crop_obj.gap_sections.all()}
        # appends the results with the GAPs to that have bbenfetched
        # The results are used in frontend with predict function acting as a bridge between cropPredict and frontend
        results.append({
            "crop": crop,
            "confidence": float(conf),
            "image": imagePath,
            "gap": gap_data  # Include GAP data
        })
    return results

# Predict view 
@csrf_exempt
def predict(request):
    if request.method == "POST": #once you presss the predict button
        try:
            data = json.loads(request.body)
            constituency = data.get("constituency", "").strip().lower()
            ward = data.get("ward", "").strip().lower()
            
            # If constituency and wards are missing (All should be filled)
            if not (constituency and ward):
                return JsonResponse({"error": "Fill all fields"}, status=400)
            
            locationQuery = f"{ward}, {constituency}, Kenya" #chosen ward and constituency
         # Geolocation APIs defined
                    
            apiKeys = [
                # os.getenv("locationAPI1"), These are correct APIs uncomment them to work as expected
                # os.getenv("locationAPI2"),
                os.getenv("FakeAPI")#fake api
            ]
            # Fetches location co-ordinates from the names that have been passed
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
                return None #do not return anything if it fails
            
            coordinates = None
            for apiKey in apiKeys:#for every API key defined try all of them
                coordinates = fetchCoordinates(apiKey) #calls the function to get the coOrdinates passing in the keys
                if coordinates: #continue if coordinates found and proceed to call cropsPrediction
                    print("Yayy location coordinates found")#Debug line
                    break
            
            if not coordinates: #if not found in API resort to Excel Backup file
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
            
            # Calls the Crop Prediction View and passes the coordinates found, Stores the result in cropResults
            crop_results = cropPrediction(coordinates["lat"], coordinates["lng"])
            
            # Returns this result to frontend that is coordinates and crop_results gotten from cropPrediction function that was called
            return JsonResponse({
                "coordinates": coordinates,
                "crop_predictions": crop_results #results from cropPrediction function
            })
        
        except Exception as e: #when an error occurs 
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