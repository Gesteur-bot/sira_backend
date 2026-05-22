from django.contrib import admin
from .models import SOSAlert


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "user", "alert_type", "status",
        "ride", "responded_by",
        "emergency_contact_notified",
        "created_at", "resolved_at"
    )
    list_filter   = ("alert_type", "status", "emergency_contact_notified")
    search_fields = ("user__phone_number",)
    raw_id_fields = ("user", "ride", "responded_by")