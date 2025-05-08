from django.urls import path
from . import views

#Specifies the different views that have been specified in
# Homepage-views.py
urlpatterns = [
    path('Homepage/', views.Homepage, name='Homepage'),
    path('countyLoad/', views.countyLoad, name='countyLoad'),
    path('subcountyLoad/', views.subcountyLoad, name='subcountyLoad'),
    path('wardLoad/', views.wardLoad, name='wardLoad'),
    path("predict/", views.predict, name="predict"),
   
]