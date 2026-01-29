from django.contrib import admin
from django.urls import path
from core.views import home, inscricao_view
from ai_chat.views import chatbot_view, chatbot_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("inscricao/", inscricao_view, name="inscricao"),
    path("chat/", chatbot_page, name="chatbot_page"),      # Página HTML
    path("api/chatbot/", chatbot_view, name="chatbot_api"), # API
]
