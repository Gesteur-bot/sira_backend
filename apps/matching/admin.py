from django.contrib import admin
from .models import MatchingConfiguration


@admin.register(MatchingConfiguration)
class MatchingConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "weight_distance", "weight_quality", "weight_waiting_time",
        "score_threshold_warning", "score_threshold_suspension",
        "initial_search_radius_m", "max_search_radius_m",
        "dispatch_batch_size", "driver_response_timeout_s",
        "is_active", "activated_at",
    )
    list_filter  = ("is_active",)
    search_fields = ("name",)