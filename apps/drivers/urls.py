"""
URLs des profils et conducteurs Sira.
"""
from django.urls import path

from .views import (
    AdminPendingDriversView,
    AdminValidateDriverView,
    ClientProfileView,
    DriverAvailabilityView,
    DriverDocumentView,
    DriverLocationView,
    DriverProfileView,
)

urlpatterns = [
    # Client
    path("client/profile/",          ClientProfileView.as_view(),       name="client-profile"),

    # Driver
    path("driver/profile/",          DriverProfileView.as_view(),       name="driver-profile"),
    path("driver/location/",         DriverLocationView.as_view(),      name="driver-location"),
    path("driver/availability/",     DriverAvailabilityView.as_view(),  name="driver-availability"),
    path("driver/documents/",        DriverDocumentView.as_view(),      name="driver-documents"),

    # Admin
    path("admin/pending/",           AdminPendingDriversView.as_view(), name="admin-pending-drivers"),
    path("admin/<int:pk>/validate/", AdminValidateDriverView.as_view(), name="admin-validate-driver"),
]