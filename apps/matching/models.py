"""
Modèles de configuration du matching Sira.
- MatchingConfiguration : paramètres de l'algorithme de mise en relation
  conducteur ↔ client. Configurable par l'admin sans redéploiement.
  Une seule configuration active à la fois.
"""
from django.db import models

from apps.core.models import TimestampedModel


class MatchingConfiguration(TimestampedModel):

    name                      = models.CharField(max_length=100)

    # Pondération du score (somme doit = 1.0)
    weight_distance           = models.DecimalField(
                                    max_digits=4, decimal_places=3,
                                    default=0.550
                                )
    weight_quality            = models.DecimalField(
                                    max_digits=4, decimal_places=3,
                                    default=0.300
                                )
    weight_waiting_time       = models.DecimalField(
                                    max_digits=4, decimal_places=3,
                                    default=0.150
                                )

    # Seuils de score
    score_threshold_warning    = models.DecimalField(
                                     max_digits=5, decimal_places=2,
                                     default=50.00
                                 )
    score_threshold_suspension = models.DecimalField(
                                     max_digits=5, decimal_places=2,
                                     default=30.00
                                 )

    # Rayon de recherche
    max_search_radius_m        = models.PositiveIntegerField(default=5000)
    initial_search_radius_m    = models.PositiveIntegerField(default=1000)

    # Dispatch
    dispatch_batch_size        = models.PositiveSmallIntegerField(default=3)
    driver_response_timeout_s  = models.PositiveSmallIntegerField(default=15)
    total_dispatch_timeout_s   = models.PositiveSmallIntegerField(default=90)

    is_active                  = models.BooleanField(default=False)
    activated_at               = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table        = "sira_matching_config"
        verbose_name    = "Configuration matching"
        verbose_name_plural = "Configurations matching"
        # Une seule configuration active à la fois
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="unique_active_matching_config",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"