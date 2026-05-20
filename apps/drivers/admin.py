from django.contrib import admin
from .models import ClientProfile, DriverProfile, AdminProfile, Vehicle, DriverDocument, DriverScore


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "client_score", "total_rides", "created_at")
    search_fields = ("first_name", "last_name")


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "validation_status", "is_available", "current_score", "is_in_matching_suspension")
    list_filter   = ("validation_status", "is_available", "is_in_matching_suspension", "mobile_money_operator")
    search_fields = ("first_name", "last_name")
    raw_id_fields = ("validated_by",)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "email", "department", "position")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display  = ("license_plate", "vehicle_type", "brand", "model", "color", "driver", "is_active")
    list_filter   = ("vehicle_type", "is_active")
    search_fields = ("license_plate", "brand")


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    list_display  = ("driver", "document_type", "verification_status", "expiry_date", "created_at")
    list_filter   = ("document_type", "verification_status")
    raw_id_fields = ("verified_by",)


@admin.register(DriverScore)
class DriverScoreAdmin(admin.ModelAdmin):
    list_display  = ("driver", "overall_score", "rating_score", "acceptance_score", "completion_score", "computed_at")
    list_filter   = ("computation_period_start",)