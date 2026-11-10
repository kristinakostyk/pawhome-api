from .views import RegisterAPIView, ProfileAPIView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterAPIView
from .views import RegisterAPIView, ProfileAPIView, LogoutAPIView

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name="register"),
    path("login", TokenObtainPairView.as_view(), name="login"),
    path("refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("me", ProfileAPIView.as_view(), name="profile"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
]
