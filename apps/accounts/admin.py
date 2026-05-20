from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PhoneVerificationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ("phone_number", "role", "is_phone_verified", "is_suspended", "is_active", "created_at")
    list_filter   = ("role", "is_phone_verified", "is_suspended", "is_active")
    search_fields = ("phone_number",)
    ordering      = ("-created_at",)

    fieldsets = (
        (None,          {"fields": ("phone_number", "password")}),
        ("Rôle",        {"fields": ("role",)}),
        ("Vérification",{"fields": ("is_phone_verified", "phone_verified_at")}),
        ("Suspension",  {"fields": ("is_suspended", "suspension_reason", "suspended_until")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "role", "password1", "password2"),
        }),
    )


@admin.register(PhoneVerificationCode)
class PhoneVerificationCodeAdmin(admin.ModelAdmin):
    list_display  = ("phone_number", "is_used", "attempts", "max_attempts", "expires_at", "created_at")
    list_filter   = ("is_used",)
    search_fields = ("phone_number",)