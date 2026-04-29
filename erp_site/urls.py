from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.templatetags.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
    path("ai_chat/", include("ai_chat.urls")),
    path("favicon.ico", RedirectView.as_view(url=static("images/favicon.ico"), permanent=True)),
]
