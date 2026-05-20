"""
Modèles abstraits partagés par toutes les apps Sira.
"""
import uuid
from django.db import models


class TimestampedModel(models.Model):
    """Ajoute created_at et updated_at automatiquement."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Remplace l'id BigAutoField par un UUID v4."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class UUIDTimestampedModel(UUIDModel, TimestampedModel):
    """UUID + timestamps — utilisé pour Ride, Payment, DriverPayout."""
    class Meta:
        abstract = True