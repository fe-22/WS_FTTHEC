from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('api/', views.chatbot_view, name='chatbot_api'),
    path('lead/', views.save_chat_lead, name='save_chat_lead'),
    path('analytics/', views.chat_analytics, name='chat_analytics'),
]