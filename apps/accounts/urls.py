"""
URLs d'authentification Sira.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginVerifyView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    VerifyOTPView,
)

urlpatterns = [
    path("register/",       RegisterView.as_view(),     name="auth-register"),
    path("verify-otp/",     VerifyOTPView.as_view(),    name="auth-verify-otp"),
    path("login/",          LoginView.as_view(),        name="auth-login"),
    path("login/verify/",   LoginVerifyView.as_view(),  name="auth-login-verify"),
    path("token/refresh/",  TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("logout/",         LogoutView.as_view(),       name="auth-logout"),
    path("me/",             MeView.as_view(),           name="auth-me"),
]