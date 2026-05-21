from django.contrib import admin
from .models import LegalDocument, UserAcceptance


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display  = ("document_type", "version", "title", "is_active", "effective_from", "created_by")
    list_filter   = ("document_type", "is_active")
    search_fields = ("title", "version")
    raw_id_fields = ("created_by",)


@admin.register(UserAcceptance)
class UserAcceptanceAdmin(admin.ModelAdmin):
    list_display  = ("user", "document", "acceptance_method", "ip_address", "accepted_at")
    list_filter   = ("acceptance_method", "document__document_type")
    search_fields = ("user__phone_number",)
    raw_id_fields = ("user", "document")