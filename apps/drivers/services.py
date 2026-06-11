"""
Services métier des conducteurs Sira.
"""
from django.utils import timezone
from django.contrib.gis.geos import Point

from .models import ClientProfile, DriverProfile, DriverDocument


def create_client_profile(user, data):
    """Crée le profil client après inscription."""
    if hasattr(user, "client_profile"):
        return False, "Profil client déjà existant."

    profile = ClientProfile.objects.create(
        user=user,
        **data
    )
    return True, profile


def update_client_profile(user, data):
    """Met à jour le profil client."""
    try:
        profile = user.client_profile
    except ClientProfile.DoesNotExist:
        return False, "Profil introuvable."

    for field, value in data.items():
        setattr(profile, field, value)
    profile.save()

    return True, profile


def create_driver_profile(user, data):
    """Crée le profil conducteur après inscription."""
    if hasattr(user, "driver_profile"):
        return False, "Profil conducteur déjà existant."

    profile = DriverProfile.objects.create(
        user=user,
        **data
    )
    return True, profile


def update_driver_location(driver_profile, latitude, longitude):
    """Met à jour la position GPS du conducteur."""
    driver_profile.current_location = Point(longitude, latitude, srid=4326)
    driver_profile.last_location_update = timezone.now()
    driver_profile.save(update_fields=["current_location", "last_location_update"])
    return True


def update_driver_availability(driver_profile, is_available):
    """Active ou désactive la disponibilité du conducteur."""
    # Un conducteur suspendu ne peut pas se rendre disponible
    if is_available and driver_profile.is_in_matching_suspension:
        return False, "Votre compte est suspendu du matching."

    # Un conducteur non validé ne peut pas se rendre disponible
    if is_available and not driver_profile.is_validated:
        return False, "Votre compte n'est pas encore validé."

    driver_profile.is_available = is_available
    driver_profile.save(update_fields=["is_available"])
    return True, None


def validate_driver(driver_profile, action, rejection_reason=None, validated_by=None):
    """Valide ou rejette un conducteur (admin)."""
    if action == "approve":
        driver_profile.validation_status = DriverProfile.ValidationStatus.APPROVED
        driver_profile.validated_at      = timezone.now()
        driver_profile.validated_by      = validated_by
        driver_profile.rejection_reason  = ""
    elif action == "reject":
        driver_profile.validation_status = DriverProfile.ValidationStatus.REJECTED
        driver_profile.rejection_reason  = rejection_reason

    driver_profile.save(update_fields=[
        "validation_status",
        "validated_at",
        "validated_by",
        "rejection_reason",
    ])
    return True, driver_profile