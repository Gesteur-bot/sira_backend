"""
Services des courses Sira.
- Création de course
- Transitions de statut
- Anti-fraude GPS
- Sync offline
"""
from decimal import Decimal
from django.conf import settings
from django.contrib.gis.geos import Point, LineString
from django.utils import timezone

from apps.pricing.services import calculate_price, calculate_final_price
from apps.drivers.models import ClientProfile, DriverProfile

from .models import Ride, GPSPoint


def create_ride(user, data):
    """
    Crée une nouvelle course.
    Calcule le prix estimé via PricingRule active.
    """
    try:
        client_profile = user.client_profile
    except ClientProfile.DoesNotExist:
        return None, "Profil client introuvable. Complétez votre profil d'abord."

    # Points GPS
    pickup_location  = Point(data["pickup_longitude"],  data["pickup_latitude"],  srid=4326)
    dropoff_location = Point(data["dropoff_longitude"], data["dropoff_latitude"], srid=4326)

    # Calcul prix estimé
    is_night = _is_night_hour()
    price_result, error = calculate_price(
        service_type = data["service_type"],
        vehicle_type = data["vehicle_type"],
        distance_m   = data["estimated_distance_m"],
        is_night     = is_night,
        package_size = data.get("package_size"),
        is_urgent    = data.get("is_urgent", False),
    )

    if error:
        return None, f"Impossible de calculer le tarif : {error}"

    estimated_price  = price_result["estimated_price"]
    pricing_snapshot = price_result

    # Créer la course
    ride = Ride.objects.create(
        client               = client_profile,
        service_type         = data["service_type"],
        selection_method     = data.get("selection_method", "AUTO_DISPATCH"),
        pickup_location      = pickup_location,
        pickup_address       = data.get("pickup_address", ""),
        dropoff_location     = dropoff_location,
        dropoff_address      = data.get("dropoff_address", ""),
        estimated_distance_m = data["estimated_distance_m"],
        estimated_price      = estimated_price,
        pricing_snapshot     = pricing_snapshot,
        recipient_phone      = data.get("recipient_phone", ""),
        recipient_name       = data.get("recipient_name", ""),
        package_description  = data.get("package_description", ""),
        package_size         = data.get("package_size", ""),
        package_weight_kg    = data.get("package_weight_kg"),
        package_is_fragile   = data.get("package_is_fragile", False),
        package_value_fcfa   = data.get("package_value_fcfa"),
        is_urgent            = data.get("is_urgent", False),
        forbidden_content_certified = data.get("forbidden_content_certified", False),
        client_local_id      = data.get("client_local_id", ""),
    )

    return ride, None


def accept_ride(ride, driver_user):
    """Le conducteur accepte une course."""
    if ride.status != Ride.Status.REQUESTED:
        return False, "Cette course n'est plus disponible."

    try:
        driver_profile = driver_user.driver_profile
    except DriverProfile.DoesNotExist:
        return False, "Profil conducteur introuvable."

    if not driver_profile.is_validated:
        return False, "Votre compte n'est pas validé."

    if not driver_profile.is_available:
        return False, "Vous n'êtes pas disponible."

    # Récupérer le véhicule actif
    vehicle = driver_profile.vehicles.filter(is_active=True).first()
    if not vehicle:
        return False, "Aucun véhicule actif trouvé."

    ride.driver      = driver_profile
    ride.vehicle     = vehicle
    ride.status      = Ride.Status.ACCEPTED
    ride.accepted_at = timezone.now()
    ride.save(update_fields=["driver", "vehicle", "status", "accepted_at"])

    # Mettre conducteur non disponible
    driver_profile.is_available = False
    driver_profile.save(update_fields=["is_available"])

    return True, ride


def driver_arrived(ride, driver_user):
    """Le conducteur est arrivé au point de pickup."""
    if ride.status != Ride.Status.ACCEPTED:
        return False, "Statut de course invalide."

    if ride.driver.user != driver_user:
        return False, "Vous n'êtes pas le conducteur de cette course."

    ride.status           = Ride.Status.ACCEPTED
    ride.driver_arrived_at = timezone.now()
    ride.save(update_fields=["driver_arrived_at"])

    return True, ride


def start_ride(ride, driver_user):
    """Démarre la course."""
    if ride.status != Ride.Status.ACCEPTED:
        return False, "Statut de course invalide."

    if ride.driver.user != driver_user:
        return False, "Vous n'êtes pas le conducteur de cette course."

    ride.status     = Ride.Status.IN_PROGRESS
    ride.started_at = timezone.now()
    ride.save(update_fields=["status", "started_at"])

    return True, ride


def complete_ride(ride, driver_user, actual_distance_m):
    """
    Termine la course.
    Calcule le prix final basé sur la distance GPS réelle.
    Vérifie l'anti-fraude.
    """
    if ride.status != Ride.Status.IN_PROGRESS:
        return False, "Statut de course invalide."

    if ride.driver.user != driver_user:
        return False, "Vous n'êtes pas le conducteur de cette course."

    # Anti-fraude : comparer distance GPS vs estimée
    fraud_flags  = []
    is_flagged   = False
    fraud_score  = Decimal("0")
    tolerance    = settings.SIRA_DISTANCE_FRAUD_TOLERANCE

    if ride.estimated_distance_m > 0:
        ecart = abs(actual_distance_m - ride.estimated_distance_m) / ride.estimated_distance_m
        if ecart > tolerance:
            fraud_flags.append(f"Distance GPS ({actual_distance_m}m) vs estimée ({ride.estimated_distance_m}m) : écart {round(ecart*100, 1)}%")
            is_flagged  = True
            fraud_score = Decimal(str(min(ecart, 1.0)))

    # Calcul prix final
    is_night = _is_night_hour()
    price_result, _ = calculate_final_price(
        service_type      = ride.service_type,
        vehicle_type      = ride.vehicle.vehicle_type if ride.vehicle else "MOTO_2W",
        actual_distance_m = actual_distance_m,
        is_night          = is_night,
        package_size      = ride.package_size or None,
        is_urgent         = ride.is_urgent,
    )

    final_price = price_result["estimated_price"] if price_result else ride.estimated_price

    # Construire la route réelle depuis les points GPS
    gps_points = ride.gps_points.order_by("recorded_at")
    actual_route = None
    if gps_points.count() >= 2:
        coords = [(p.location.x, p.location.y) for p in gps_points]
        actual_route = LineString(coords, srid=4326)

    ride.status           = Ride.Status.COMPLETED
    ride.completed_at     = timezone.now()
    ride.actual_distance_m = actual_distance_m
    ride.final_price      = final_price
    ride.fraud_flags      = fraud_flags
    ride.is_flagged       = is_flagged
    ride.fraud_score      = fraud_score
    if actual_route:
        ride.actual_route = actual_route

    ride.save(update_fields=[
        "status", "completed_at", "actual_distance_m",
        "final_price", "fraud_flags", "is_flagged",
        "fraud_score", "actual_route",
    ])

    # Remettre conducteur disponible + stats
    driver_profile = ride.driver
    driver_profile.is_available            = True
    driver_profile.last_ride_completed_at  = timezone.now()
    driver_profile.total_rides            += 1
    driver_profile.total_completed_rides  += 1
    driver_profile.save(update_fields=[
        "is_available", "last_ride_completed_at",
        "total_rides", "total_completed_rides",
    ])

    return True, ride


def cancel_ride(ride, user, cancellation_reason=""):
    """Annule une course."""
    if ride.status in [Ride.Status.COMPLETED, Ride.Status.CANCELLED]:
        return False, "Cette course ne peut plus être annulée."

    ride.status              = Ride.Status.CANCELLED
    ride.cancelled_at        = timezone.now()
    ride.cancelled_by        = user
    ride.cancellation_reason = cancellation_reason
    ride.save(update_fields=[
        "status", "cancelled_at", "cancelled_by", "cancellation_reason"
    ])

    # Si un conducteur était assigné, le remettre disponible
    if ride.driver:
        ride.driver.is_available = True
        ride.driver.save(update_fields=["is_available"])
        ride.driver.total_cancelled_rides += 1
        ride.driver.save(update_fields=["total_cancelled_rides"])

    return True, ride


def add_gps_point(ride, data):
    """
    Ajoute un point GPS à une course.
    Vérifie la vitesse et la cohérence.
    """
    if ride.status != Ride.Status.IN_PROGRESS:
        return False, "La course n'est pas en cours."

    location      = Point(data["longitude"], data["latitude"], srid=4326)
    is_suspect    = False
    suspect_reasons = []

    # Vérifier vitesse anormale
    if data.get("speed_kmh") and data["speed_kmh"] > settings.SIRA_MAX_REASONABLE_SPEED_KMH:
        is_suspect = True
        suspect_reasons.append(f"Vitesse anormale : {data['speed_kmh']} km/h")

    # Vérifier précision GPS
    if data["accuracy_m"] > settings.SIRA_MIN_GPS_ACCURACY_M:
        is_suspect = True
        suspect_reasons.append(f"Précision GPS faible : {data['accuracy_m']}m")

    gps_point = GPSPoint.objects.create(
        ride                 = ride,
        location             = location,
        accuracy_m           = data["accuracy_m"],
        speed_kmh            = data.get("speed_kmh"),
        bearing              = data.get("bearing"),
        recorded_at          = data["recorded_at"],
        is_from_offline_sync = data.get("is_from_offline_sync", False),
        is_suspect           = is_suspect,
        suspect_reasons      = suspect_reasons,
    )

    return True, gps_point


def _is_night_hour():
    """Vérifie si on est dans la plage horaire de nuit."""
    now  = timezone.now()
    hour = now.hour
    return hour >= 22 or hour < 5