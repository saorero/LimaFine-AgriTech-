import requests
from django.shortcuts import render
from django.http import HttpResponse
import random


# Create your views here.
# Views for Resource applicatio
def fetchVideos(query="agriculture", maxResults=12):

    # youtubeApi = "AIzaSyCr_qmPHd8KjokbV8Ww90v8evqrk8Zrwl4"
    youtubeApi = "AIzaSyCr_qmPHd8KjokbV8Ww90v8evqrk8Zrwl" #limits API usage
    youtubeSearch = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": maxResults,
        "key": youtubeApi,
    }
    response = requests.get(youtubeSearch, params=params) #Request sent to youtube
    
    if response.status_code == 200:
        videos = response.json().get("items", [])
        return [
            {
                "title": video["snippet"]["title"],
                "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"],
                "video_id": video["id"]["videoId"],
            }
            for video in videos
        ]
    else:
        #To handle API fail      
        return {"error": "An unknown error occurred while fetching videos."}


# Function to handle video requests
def videoSection(request):
    query = request.GET.get("q", None) #search items defined by user
    if query is None: #if not defined by user pick searches at random
        query = random.choice(["agriculture", "farming", "crops", "soil health", "organic farming", "agriculture kenya"])
    videos = fetchVideos(query) #fetch related video content
    return render(request, "resource.html", {"videos": videos}) #send videos to the frontend template


def articles(request):
    print("Hello world")
    return render(request, 'resource.html')

def hub(request):

    # return render(request, 'resource.html')
    context = {'message': 'Welcome to the Hub!'}
    return render(request, 'resource.html', context)
