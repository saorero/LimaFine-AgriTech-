
# This is created for Agricultural Bot Functionality 

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def agriBot(request):
    # return HttpResponse("Hello world!")
    return render(request, 'agriBot.html')
