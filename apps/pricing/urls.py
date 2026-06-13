"""
URLs tarifaires Sira.
"""
from django.urls import path
from .views import PriceEstimateView, PricingRuleListView

urlpatterns = [
    path("rules/",    PricingRuleListView.as_view(), name="pricing-rules"),
    path("estimate/", PriceEstimateView.as_view(),   name="pricing-estimate"),
]