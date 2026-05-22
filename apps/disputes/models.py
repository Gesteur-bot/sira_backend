"""
Modèles de litiges Sira.
- Dispute : litige sur une course (réclamation client ou conducteur).
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel
from apps.rides.models import Ride


class Dispute(TimestampedModel):

    class Status(models.TextChoices):
        OPEN             = "OPEN",             "Ouvert"
        INVESTIGATING    = "INVESTIGATING",    "En cours d'investigation"
        RESOLVED_CLIENT  = "RESOLVED_CLIENT",  "Résolu en faveur du client"
        RESOLVED_DRIVER  = "RESOLVED_DRIVER",  "Résolu en faveur du conducteur"
        DISMISSED        = "DISMISSED",        "Rejeté"

    ride        = models.ForeignKey(
                      Ride,
                      on_delete=models.PROTECT,
                      related_name="disputes",
                  )
    raised_by   = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.PROTECT,
                      related_name="disputes_raised",
                  )
    reason      = models.TextField()
    status      = models.CharField(
                      max_length=20,
                      choices=Status.choices,
                      default=Status.OPEN,
                  )
    handled_by  = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      related_name="disputes_handled",
                  )
    resolution_note  = models.TextField(blank=True)
    refund_amount    = models.DecimalField(
                           max_digits=10, decimal_places=2,
                           null=True, blank=True
                       )
    resolved_at      = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table        = "sira_dispute"
        verbose_name    = "Litige"
        verbose_name_plural = "Litiges"
        ordering        = ["-created_at"]
        indexes         = [
            models.Index(fields=["status"]),
            models.Index(fields=["ride"]),
        ]

    def __str__(self):
        return f"Dispute {self.id} — {self.ride} [{self.status}]"