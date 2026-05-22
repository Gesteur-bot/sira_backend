from django.contrib import admin
from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display  = (
        "ride", "rater", "rated",
        "score", "is_flagged", "is_hidden",
        "created_at"
    )
    list_filter   = ("score", "is_flagged", "is_hidden")
    search_fields = ("rater__phone_number", "rated__phone_number")
    raw_id_fields = ("ride", "rater", "rated")