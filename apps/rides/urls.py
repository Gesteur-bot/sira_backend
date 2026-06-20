"""
URLs des courses Sira.
"""
from django.urls import path
from .views import (
    RideAcceptView,
    RideArrivedView,
    RideCancelView,
    RideCompleteView,
    RideDetailView,
    RideGPSPointView,
    RideListCreateView,
    RideStartView,
    RideAvailableView,
)

urlpatterns = [
    path("",                      RideListCreateView.as_view(), name="ride-list-create"),
    path("available/",            RideAvailableView.as_view(),  name="ride-available"),
    path("<uuid:pk>/",            RideDetailView.as_view(),     name="ride-detail"),
    path("<uuid:pk>/accept/",     RideAcceptView.as_view(),     name="ride-accept"),
    path("<uuid:pk>/arrived/",    RideArrivedView.as_view(),    name="ride-arrived"),
    path("<uuid:pk>/start/",      RideStartView.as_view(),      name="ride-start"),
    path("<uuid:pk>/complete/",   RideCompleteView.as_view(),   name="ride-complete"),
    path("<uuid:pk>/cancel/",     RideCancelView.as_view(),     name="ride-cancel"),
    path("<uuid:pk>/gps/",        RideGPSPointView.as_view(),   name="ride-gps"),
]