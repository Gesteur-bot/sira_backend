"""
Serializers des profils et conducteurs Sira.
"""
from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import ClientProfile, DriverProfile, Vehicle, DriverDocument, DriverScore


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClientProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
            "email",
            "preferred_payment_method",
            "total_rides",
            "client_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["total_rides", "client_score", "created_at", "updated_at"]


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DriverProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
            "mobile_money_number",
            "mobile_money_operator",
            "validation_status",
            "validated_at",
            "rejection_reason",
            "is_available",
            "current_score",
            "is_in_matching_suspension",
            "total_rides",
            "total_completed_rides",
            "total_cancelled_rides",
            "average_rating",
            "total_ratings",
            "preferred_direction_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "validation_status",
            "validated_at",
            "rejection_reason",
            "is_available",
            "current_score",
            "is_in_matching_suspension",
            "total_rides",
            "total_completed_rides",
            "total_cancelled_rides",
            "average_rating",
            "total_ratings",
            "created_at",
            "updated_at",
        ]


class DriverProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création du profil conducteur."""
    class Meta:
        model  = DriverProfile
        fields = [
            "first_name",
            "last_name",
            "photo",
            "mobile_money_number",
            "mobile_money_operator",
        ]


class LocationUpdateSerializer(serializers.Serializer):
    """Mise à jour position GPS du conducteur."""
    latitude  = serializers.FloatField()
    longitude = serializers.FloatField()

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude invalide.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude invalide.")
        return value


class AvailabilitySerializer(serializers.Serializer):
    """Activer/désactiver disponibilité conducteur."""
    is_available = serializers.BooleanField()


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vehicle
        fields = [
            "id",
            "vehicle_type",
            "license_plate",
            "brand",
            "model",
            "color",
            "year",
            "passenger_capacity",
            "cargo_capacity",
            "required_license_type",
            "photo",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class DriverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DriverDocument
        fields = [
            "id",
            "document_type",
            "file",
            "issued_date",
            "expiry_date",
            "verification_status",
            "verified_at",
            "rejection_reason",
            "created_at",
        ]
        read_only_fields = [
            "verification_status",
            "verified_at",
            "rejection_reason",
            "created_at",
        ]


class DriverScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DriverScore
        fields = [
            "overall_score",
            "rating_score",
            "acceptance_score",
            "completion_score",
            "seniority_score",
            "incident_score",
            "computed_at",
            "computation_period_start",
            "computation_period_end",
            "rides_evaluated_count",
        ]
        read_only_fields = fields


class DriverValidationSerializer(serializers.Serializer):
    """Serializer pour valider ou rejeter un conducteur (admin)."""
    action           = serializers.ChoiceField(choices=["approve", "reject"])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["action"] == "reject" and not data.get("rejection_reason"):
            raise serializers.ValidationError(
                {"rejection_reason": "Le motif est obligatoire en cas de rejet."}
            )
        return data