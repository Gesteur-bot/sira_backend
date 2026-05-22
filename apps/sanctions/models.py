"""
Modèles de sanctions Sira.
- UserSanction : sanctions graduées avec procédure d'appel.
  Peut concerner un client OU un conducteur.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel
from apps.rides.models import Ride


class UserSanction(TimestampedModel):

    class SanctionType(models.TextChoices):
        WARNING          = "WARNING",          "Avertissement"
        TEMP_SUSPEND     = "TEMP_SUSPEND",     "Suspension temporaire"
        PERMANENT_BAN    = "PERMANENT_BAN",    "Bannissement définitif"
        FIN_PENALTY      = "FIN_PENALTY",      "Pénalité financière"

    user            = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.PROTECT,
                          related_name="sanctions_received",
                      )
    sanction_type   = models.CharField(
                          max_length=20,
                          choices=SanctionType.choices
                      )
    reason          = models.TextField()
    related_ride    = models.ForeignKey(
                          Ride,
                          on_delete=models.SET_NULL,
                          null=True, blank=True,
                          related_name="sanctions",
                      )
    starts_at       = models.DateTimeField()
    ends_at         = models.DateTimeField(null=True, blank=True)  # NULL = permanent
    penalty_amount  = models.DecimalField(
                          max_digits=10, decimal_places=2,
                          null=True, blank=True
                      )
    issued_by       = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.PROTECT,
                          related_name="sanctions_issued",
                      )

    # Procédure d'appel
    is_appealed          = models.BooleanField(default=False)
    appeal_text          = models.TextField(blank=True)
    appeal_resolution    = models.TextField(blank=True)
    appeal_resolved_at   = models.DateTimeField(null=True, blank=True)

    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table        = "sira_user_sanction"
        verbose_name    = "Sanction"
        verbose_name_plural = "Sanctions"
        ordering        = ["-created_at"]
        indexes         = [
            models.Index(fields=["user"]),
            models.Index(fields=["sanction_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"Sanction {self.sanction_type} — {self.user} ({'active' if self.is_active else 'inactive'})"