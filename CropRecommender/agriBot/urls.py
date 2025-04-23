from django.urls import path
from . import views

#Views created in agriBot views.py
urlpatterns = [
    path('', views.chat, name='chat'), #called by the endpoint described in main urls /agriBot/
    path('ask/', views.ask_question, name='ask_question'),
    #Chat history urls 
    path('history/', views.get_chat_history, name='get_chat_history'),
    path('conversation/<str:conversation_id>/', views.get_conversation, name='get_conversation'),
    

    # path('agriBot/', views.agriBot, name='agriBot'),
   
]