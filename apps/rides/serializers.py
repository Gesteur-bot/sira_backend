"""
Serializers des courses Sira.
"""
from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import Ride, GPSPoint, RecipientPositionShare


class GPSPointSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GPSPoint
        fields = [
            "id",
            "location",
            "accuracy_m",
            "speed_kmh",
            "bearing",
            "recorded_at",
            "is_from_offline_sync",
            "is_suspect",
            "suspect_reasons",
        ]
        read_only_fields = ["is_suspect", "suspect_reasons"]


class GPSPointCreateSerializer(serializers.Serializer):
    """Soumission d'un point GPS pendant une course."""
    latitude             = serializers.FloatField()
    longitude            = serializers.FloatField()
    accuracy_m           = serializers.FloatField()
    speed_kmh            = serializers.FloatField(required=False, allow_null=True)
    bearing              = serializers.FloatField(required=False, allow_null=True)
    recorded_at          = serializers.DateTimeField()
    is_from_offline_sync = serializers.BooleanField(default=False)

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude invalide.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude invalide.")
        return value


class RideCreateSerializer(serializers.Serializer):
    """Création d'une course ou livraison."""
    service_type           = serializers.ChoiceField(choices=["PASSENGER", "DELIVERY"])
    vehicle_type           = serializers.ChoiceField(choices=["MOTO_2W", "MOTO_3W"])
    pickup_latitude        = serializers.FloatField()
    pickup_longitude       = serializers.FloatField()
    pickup_address         = serializers.CharField(max_length=255, required=False, allow_blank=True)
    dropoff_latitude       = serializers.FloatField()
    dropoff_longitude      = serializers.FloatField()
    dropoff_address        = serializers.CharField(max_length=255, required=False, allow_blank=True)
    estimated_distance_m   = serializers.IntegerField(min_value=1)
    selection_method       = serializers.ChoiceField(
                                 choices=["AUTO_DISPATCH", "MANUAL_SELECTION"],
                                 default="AUTO_DISPATCH"
                             )
    # Livraison
    recipient_phone        = serializers.CharField(max_length=20, required=False, allow_blank=True)
    recipient_name         = serializers.CharField(max_length=100, required=False, allow_blank=True)
    package_description    = serializers.CharField(required=False, allow_blank=True)
    package_size           = serializers.ChoiceField(
                                 choices=["SMALL", "MEDIUM", "LARGE"],
                                 required=False, allow_null=True
                             )
    package_weight_kg      = serializers.DecimalField(
                                 max_digits=5, decimal_places=2,
                                 required=False, allow_null=True
                             )
    package_is_fragile     = serializers.BooleanField(default=False)
    package_value_fcfa     = serializers.DecimalField(
                                 max_digits=10, decimal_places=2,
                                 required=False, allow_null=True
                             )
    is_urgent              = serializers.BooleanField(default=False)
    forbidden_content_certified = serializers.BooleanField(default=False)
    client_local_id        = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, data):
        if data["service_type"] == "DELIVERY":
            if not data.get("recipient_phone"):
                raise serializers.ValidationError(
                    {"recipient_phone": "Obligatoire pour une livraison."}
                )
            if not data.get("forbidden_content_certified"):
                raise serializers.ValidationError(
                    {"forbidden_content_certified": "Vous devez certifier l'absence de contenu interdit."}
                )
        return data


class RideSerializer(serializers.ModelSerializer):
    """Serializer complet d'une course."""
    class Meta:
        model  = Ride
        fields = [
            "id",
            "service_type",
            "status",
            "selection_method",
            "client",
            "driver",
            "vehicle",
            "pickup_address",
            "dropoff_address",
            "estimated_distance_m",
            "theoretical_distance_m",
            "actual_distance_m",
            "estimated_price",
            "final_price",
            "pricing_snapshot",
            "recipient_phone",
            "recipient_name",
            "package_description",
            "package_size",
            "package_weight_kg",
            "package_is_fragile",
            "package_value_fcfa",
            "is_urgent",
            "forbidden_content_certified",
            "requested_at",
            "accepted_at",
            "driver_arrived_at",
            "started_at",
            "completed_at",
            "cancelled_at",
            "cancellation_reason",
            "is_flagged",
            "fraud_score",
            "synced_from_offline",
            "client_local_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RideCancelSerializer(serializers.Serializer):
    """Annulation d'une course."""
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)


class RideCompleteSerializer(serializers.Serializer):
    """Fin d'une course avec distance réelle."""
    actual_distance_m = serializers.IntegerField(min_value=1)


class RecipientPositionShareSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RecipientPositionShare
        fields = [
            "id",
            "token",
            "recipient_phone",
            "status",
            "expires_at",
            "sms_sent_at",
        ]
        read_only_fields = fields


class OfflineRideSyncSerializer(serializers.Serializer):
    """Synchronisation d'une course enregistrée offline."""
    client_local_id        = serializers.CharField(max_length=100)
    service_type           = serializers.ChoiceField(choices=["PASSENGER", "DELIVERY"])
    vehicle_type           = serializers.ChoiceField(choices=["MOTO_2W", "MOTO_3W"])
    pickup_latitude        = serializers.FloatField()
    pickup_longitude       = serializers.FloatField()
    pickup_address         = serializers.CharField(required=False, allow_blank=True)
    dropoff_latitude       = serializers.FloatField()
    dropoff_longitude      = serializers.FloatField()
    dropoff_address        = serializers.CharField(required=False, allow_blank=True)
    estimated_distance_m   = serializers.IntegerField(min_value=1)
    actual_distance_m      = serializers.IntegerField(min_value=1)
    gps_points             = GPSPointCreateSerializer(many=True)