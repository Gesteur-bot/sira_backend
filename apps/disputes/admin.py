from django.contrib import admin
from .models import Dispute


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "ride", "raised_by", "status",
        "handled_by", "refund_amount", "resolved_at",
        "created_at"
    )
    list_filter   = ("status",)
    search_fields = ("ride__id", "raised_by__phone_number")
    raw_id_fields = ("ride", "raised_by", "handled_by")