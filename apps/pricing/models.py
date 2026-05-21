"""
Modèles tarifaires Sira.
- PricingRule : règles tarifaires versionnées.
  On ne modifie JAMAIS une règle existante : on crée une nouvelle version.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class PricingRule(TimestampedModel):

    class ServiceType(models.TextChoices):
        PASSENGER = "PASSENGER", "Course passager"
        DELIVERY  = "DELIVERY",  "Livraison"

    class VehicleType(models.TextChoices):
        MOTO_2W = "MOTO_2W", "Moto 2 roues"
        MOTO_3W = "MOTO_3W", "Moto 3 roues"

    name                         = models.CharField(max_length=100)
    service_type                 = models.CharField(
                                       max_length=10,
                                       choices=ServiceType.choices
                                   )
    vehicle_type                 = models.CharField(
                                       max_length=10,
                                       choices=VehicleType.choices
                                   )
    base_fare                    = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_km                 = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_fare                 = models.DecimalField(max_digits=10, decimal_places=2)

    # Surcharge nuit
    night_surcharge_percent      = models.DecimalField(
                                       max_digits=5, decimal_places=2,
                                       default=0
                                   )
    night_start_hour             = models.PositiveSmallIntegerField(default=22)
    night_end_hour               = models.PositiveSmallIntegerField(default=5)

    # Surcharges livraison
    delivery_size_surcharge      = models.JSONField(default=dict)
    delivery_urgency_surcharge_percent = models.DecimalField(
                                             max_digits=5, decimal_places=2,
                                             default=0
                                         )

    is_active                    = models.BooleanField(default=False)
    valid_from                   = models.DateTimeField()
    valid_until                  = models.DateTimeField(null=True, blank=True)

    created_by                   = models.ForeignKey(
                                       settings.AUTH_USER_MODEL,
                                       on_delete=models.PROTECT,
                                       related_name="created_pricing_rules",
                                   )

    class Meta:
        db_table        = "sira_pricing_rule"
        verbose_name    = "Règle tarifaire"
        verbose_name_plural = "Règles tarifaires"
        # Une seule règle active par (service_type, vehicle_type)
        constraints = [
            models.UniqueConstraint(
                fields=["service_type", "vehicle_type"],
                condition=models.Q(is_active=True),
                name="unique_active_pricing_per_service_vehicle",
            ),
        ]

    def __str__(self):
        return f"{self.name} — {self.service_type}/{self.vehicle_type} ({'active' if self.is_active else 'inactive'})"