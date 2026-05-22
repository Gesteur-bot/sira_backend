from django.contrib import admin
from .models import UserSanction


@admin.register(UserSanction)
class UserSanctionAdmin(admin.ModelAdmin):
    list_display  = (
        "user", "sanction_type", "reason",
        "starts_at", "ends_at",
        "is_appealed", "is_active",
        "issued_by", "created_at"
    )
    list_filter   = ("sanction_type", "is_active", "is_appealed")
    search_fields = ("user__phone_number", "issued_by__phone_number")
    raw_id_fields = ("user", "issued_by", "related_ride")