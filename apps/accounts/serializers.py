"""
Serializers d'authentification Sira.
"""
from django.conf import settings
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region="BF")
    role         = serializers.ChoiceField(choices=User.Role.choices)

    def validate_role(self, value):
        # On ne peut pas s'inscrire comme ADMIN via l'API
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "L'inscription en tant qu'administrateur n'est pas autorisée."
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region="BF")
    code         = serializers.CharField(max_length=6, min_length=6)


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region="BF")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            "id",
            "phone_number",
            "role",
            "is_phone_verified",
            "is_suspended",
            "created_at",
        ]
        read_only_fields = fields