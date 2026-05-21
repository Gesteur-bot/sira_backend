from django.contrib import admin
from .models import PricingRule


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display  = (
        "name", "service_type", "vehicle_type",
        "base_fare", "price_per_km", "minimum_fare",
        "is_active", "valid_from"
    )
    list_filter   = ("service_type", "vehicle_type", "is_active")
    search_fields = ("name",)
    raw_id_fields = ("created_by",)