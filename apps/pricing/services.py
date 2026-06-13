"""
Services tarifaires Sira.
Calcul du prix estimé et du prix final d'une course.
"""
from decimal import Decimal
from .models import PricingRule


def get_active_pricing_rule(service_type, vehicle_type):
    """Récupère la règle tarifaire active pour un type de service et véhicule."""
    try:
        return PricingRule.objects.get(
            service_type=service_type,
            vehicle_type=vehicle_type,
            is_active=True,
        )
    except PricingRule.DoesNotExist:
        return None


def calculate_price(service_type, vehicle_type, distance_m, is_night=False,
                    package_size=None, is_urgent=False):
    """
    Calcule le prix estimé d'une course.
    Retourne un dict avec le détail du calcul.
    """
    rule = get_active_pricing_rule(service_type, vehicle_type)
    if not rule:
        return None, "Aucune règle tarifaire active pour ce type de service."

    distance_km   = Decimal(str(distance_m)) / Decimal("1000")
    base_fare     = rule.base_fare
    distance_fare = rule.price_per_km * distance_km

    # Surcharge nuit
    night_surcharge = Decimal("0")
    if is_night and rule.night_surcharge_percent > 0:
        night_surcharge = (base_fare + distance_fare) * rule.night_surcharge_percent / 100

    # Surcharge taille colis (livraison)
    size_surcharge = Decimal("0")
    if package_size and rule.delivery_size_surcharge:
        size_surcharge = Decimal(
            str(rule.delivery_size_surcharge.get(package_size, 0))
        )

    # Surcharge urgence (livraison)
    urgency_surcharge = Decimal("0")
    if is_urgent and rule.delivery_urgency_surcharge_percent > 0:
        urgency_surcharge = (base_fare + distance_fare) * \
                            rule.delivery_urgency_surcharge_percent / 100

    # Prix total
    total = base_fare + distance_fare + night_surcharge + size_surcharge + urgency_surcharge

    # Appliquer le minimum
    estimated_price = max(total, rule.minimum_fare)

    return {
        "estimated_price":   round(estimated_price, 2),
        "base_fare":         round(base_fare, 2),
        "distance_fare":     round(distance_fare, 2),
        "night_surcharge":   round(night_surcharge, 2),
        "size_surcharge":    round(size_surcharge, 2),
        "urgency_surcharge": round(urgency_surcharge, 2),
        "currency":          "FCFA",
        "pricing_rule_id":   rule.id,
    }, None


def calculate_final_price(service_type, vehicle_type, actual_distance_m,
                           is_night=False, package_size=None, is_urgent=False):
    """
    Calcule le prix final après une course basé sur la distance réelle GPS.
    Même logique que calculate_price mais avec la distance réelle.
    """
    return calculate_price(
        service_type, vehicle_type, actual_distance_m,
        is_night, package_size, is_urgent
    )