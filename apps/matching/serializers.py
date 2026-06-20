"""
Serializers du matching Sira.
"""
from rest_framework import serializers
from .models import MatchingConfiguration


class MatchingConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MatchingConfiguration
        fields = [
            "id",
            "name",
            "weight_distance",
            "weight_quality",
            "weight_waiting_time",
            "score_threshold_warning",
            "score_threshold_suspension",
            "max_search_radius_m",
            "initial_search_radius_m",
            "dispatch_batch_size",
            "driver_response_timeout_s",
            "total_dispatch_timeout_s",
            "is_active",
            "activated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["activated_at", "created_at", "updated_at"]

    def validate(self, data):
        """Vérifie que la somme des poids = 1.0"""
        weight_distance     = data.get("weight_distance", 0)
        weight_quality      = data.get("weight_quality", 0)
        weight_waiting_time = data.get("weight_waiting_time", 0)

        total = weight_distance + weight_quality + weight_waiting_time
        if abs(float(total) - 1.0) > 0.001:
            raise serializers.ValidationError(
                "La somme des poids (distance + qualité + attente) doit être égale à 1.0"
            )
        return data