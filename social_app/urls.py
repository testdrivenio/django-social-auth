from django.contrib import admin
from django.urls import path, include

from .views import Home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", Home.as_view(), name="home"),
]
