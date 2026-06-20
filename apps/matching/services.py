"""
Services de matching Sira.
Algorithme de mise en relation conducteur ↔ client.
"""
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone

from apps.drivers.models import DriverProfile
from .models import MatchingConfiguration


def get_active_config():
    """Récupère la configuration de matching active."""
    try:
        return MatchingConfiguration.objects.get(is_active=True)
    except MatchingConfiguration.DoesNotExist:
        # Valeurs par défaut depuis settings
        return None


def find_available_drivers(pickup_location, service_type=None, vehicle_type=None):
    """
    Trouve les conducteurs disponibles à proximité d'un point GPS.
    Retourne une liste triée par score de matching.

    pickup_location : tuple (latitude, longitude)
    """
    config = get_active_config()

    # Rayon de recherche
    initial_radius = (
        config.initial_search_radius_m
        if config else settings.SIRA_INITIAL_SEARCH_RADIUS_M
    )
    max_radius = (
        config.max_search_radius_m
        if config else settings.SIRA_MAX_SEARCH_RADIUS_M
    )

    # Point de départ
    point = Point(pickup_location[1], pickup_location[0], srid=4326)

    # Requête de base : conducteurs disponibles, validés, non suspendus
    queryset = DriverProfile.objects.filter(
        is_available=True,
        validation_status=DriverProfile.ValidationStatus.APPROVED,
        is_in_matching_suspension=False,
        current_location__isnull=False,
    )

    # Filtrer par rayon initial
    queryset = queryset.filter(
        current_location__distance_lte=(point, D(m=initial_radius))
    ).annotate(
        distance=Distance("current_location", point)
    )

    # Si pas assez de conducteurs, élargir jusqu'au rayon max
    if queryset.count() < 3:
        queryset = DriverProfile.objects.filter(
            is_available=True,
            validation_status=DriverProfile.ValidationStatus.APPROVED,
            is_in_matching_suspension=False,
            current_location__isnull=False,
        ).filter(
            current_location__distance_lte=(point, D(m=max_radius))
        ).annotate(
            distance=Distance("current_location", point)
        )

    # Calculer le score de matching pour chaque conducteur
    drivers_with_score = []
    for driver in queryset:
        score = calculate_matching_score(driver, config)
        drivers_with_score.append((driver, score))

    # Trier par score décroissant
    drivers_with_score.sort(key=lambda x: x[1], reverse=True)

    return [driver for driver, score in drivers_with_score]


def calculate_matching_score(driver, config=None):
    """
    Calcule le score de matching d'un conducteur.
    Score = (poids_distance × score_distance) +
            (poids_qualité × score_qualité) +
            (poids_attente × score_attente)
    """
    if not config:
        config = get_active_config()

    # Poids
    w_distance = float(config.weight_distance     if config else settings.SIRA_MATCHING_WEIGHT_DISTANCE)
    w_quality  = float(config.weight_quality      if config else settings.SIRA_MATCHING_WEIGHT_SCORE)
    w_waiting  = float(config.weight_waiting_time if config else settings.SIRA_MATCHING_WEIGHT_WAITING)

    # Score qualité (score conducteur normalisé 0-1)
    score_quality = float(driver.current_score) / 100

    # Score attente (plus le conducteur attend, plus son score monte)
    score_waiting = 0.5  # Valeur par défaut
    if driver.last_ride_completed_at:
        minutes_waiting = (
            timezone.now() - driver.last_ride_completed_at
        ).total_seconds() / 60
        score_waiting = min(minutes_waiting / 60, 1.0)  # Max 1 après 60 min

    # Score distance (inversé : plus proche = meilleur score)
    score_distance = 0.5  # Valeur par défaut si pas de distance annotée
    if hasattr(driver, "distance") and driver.distance:
        max_radius = float(config.max_search_radius_m if config else 5000)
        distance_m = driver.distance.m
        score_distance = max(0, 1 - (distance_m / max_radius))

    # Score final
    final_score = (
        w_distance * score_distance +
        w_quality  * score_quality  +
        w_waiting  * score_waiting
    )

    return round(final_score, 4)


def activate_config(config):
    """Active une configuration et désactive les autres."""
    MatchingConfiguration.objects.filter(is_active=True).update(is_active=False)
    config.is_active   = True
    config.activated_at = timezone.now()
    config.save(update_fields=["is_active", "activated_at"])
    return config