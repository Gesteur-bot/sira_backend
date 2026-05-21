from django.contrib import admin
from .models import Ride, GPSPoint, RecipientPositionShare


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "service_type", "status", "client",
        "driver", "estimated_price", "final_price",
        "is_flagged", "requested_at"
    )
    list_filter   = ("service_type", "status", "is_flagged", "synced_from_offline")
    search_fields = ("id", "client__first_name", "driver__first_name")
    raw_id_fields = ("client", "driver", "vehicle", "cancelled_by")


@admin.register(GPSPoint)
class GPSPointAdmin(admin.ModelAdmin):
    list_display  = ("ride", "accuracy_m", "speed_kmh", "is_suspect", "recorded_at")
    list_filter   = ("is_suspect", "is_from_offline_sync")
    raw_id_fields = ("ride",)


@admin.register(RecipientPositionShare)
class RecipientPositionShareAdmin(admin.ModelAdmin):
    list_display  = ("ride", "recipient_phone", "status", "sms_sent_at", "expires_at")
    list_filter   = ("status",)
    raw_id_fields = ("ride",)