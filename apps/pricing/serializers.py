"""
Serializers tarifaires Sira.
"""
from rest_framework import serializers
from .models import PricingRule


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PricingRule
        fields = [
            "id",
            "name",
            "service_type",
            "vehicle_type",
            "base_fare",
            "price_per_km",
            "minimum_fare",
            "night_surcharge_percent",
            "night_start_hour",
            "night_end_hour",
            "delivery_size_surcharge",
            "delivery_urgency_surcharge_percent",
            "is_active",
            "valid_from",
            "valid_until",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class PriceEstimateSerializer(serializers.Serializer):
    """Serializer pour estimer le prix d'une course."""
    service_type      = serializers.ChoiceField(choices=["PASSENGER", "DELIVERY"])
    vehicle_type      = serializers.ChoiceField(choices=["MOTO_2W", "MOTO_3W"])
    distance_m        = serializers.IntegerField(min_value=1)
    is_night          = serializers.BooleanField(default=False)
    package_size      = serializers.ChoiceField(
                            choices=["SMALL", "MEDIUM", "LARGE"],
                            required=False
                        )
    is_urgent         = serializers.BooleanField(default=False)


class PriceEstimateResponseSerializer(serializers.Serializer):
    """Réponse de l'estimation de prix."""
    estimated_price   = serializers.DecimalField(max_digits=10, decimal_places=2)
    base_fare         = serializers.DecimalField(max_digits=10, decimal_places=2)
    distance_fare     = serializers.DecimalField(max_digits=10, decimal_places=2)
    night_surcharge   = serializers.DecimalField(max_digits=10, decimal_places=2)
    size_surcharge    = serializers.DecimalField(max_digits=10, decimal_places=2)
    urgency_surcharge = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency          = serializers.CharField(default="FCFA")