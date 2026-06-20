"""
URLs du matching Sira.
"""
from django.urls import path
from .views import MatchingConfigActivateView, MatchingConfigListView

urlpatterns = [
    path("config/",                  MatchingConfigListView.as_view(),     name="matching-config-list"),
    path("config/<int:pk>/activate/", MatchingConfigActivateView.as_view(), name="matching-config-activate"),
]