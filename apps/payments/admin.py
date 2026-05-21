from django.contrib import admin
from .models import Payment, DriverPayout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "ride", "amount", "operator",
        "status", "webhook_signature_valid",
        "initiated_at", "completed_at"
    )
    list_filter   = ("operator", "status", "webhook_signature_valid")
    search_fields = ("id", "external_transaction_id", "idempotency_key")
    raw_id_fields = ("ride",)


@admin.register(DriverPayout)
class DriverPayoutAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "driver", "amount", "commission_amount",
        "gross_amount", "period_start", "period_end",
        "rides_count", "status"
    )
    list_filter   = ("status",)
    search_fields = ("driver__first_name", "driver__last_name")
    raw_id_fields = ("driver", "initiated_by")