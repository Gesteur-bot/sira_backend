"""
Modèles de sécurité Sira.
- SOSAlert : alerte d'urgence déclenchée via le bouton SOS de l'app.
  Peut être déclenchée par un client OU un conducteur,
  pendant une course ou hors course.
"""
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.core.models import TimestampedModel
from apps.rides.models import Ride


class SOSAlert(TimestampedModel):

    class AlertType(models.TextChoices):
        AGGRESSION = "AGGRESSION", "Agression"
        ACCIDENT   = "ACCIDENT",   "Accident"
        MEDICAL    = "MEDICAL",    "Urgence médicale"
        OTHER      = "OTHER",      "Autre"

    class Status(models.TextChoices):
        ACTIVE      = "ACTIVE",      "Active"
        RESPONDED   = "RESPONDED",   "Prise en charge"
        RESOLVED    = "RESOLVED",    "Résolue"
        FALSE_ALARM = "FALSE_ALARM", "Fausse alarme"

    user        = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.PROTECT,
                      related_name="sos_alerts",
                  )
    ride        = models.ForeignKey(
                      Ride,
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      related_name="sos_alerts",
                  )
    alert_type  = models.CharField(
                      max_length=20,
                      choices=AlertType.choices
                  )
    location    = gis_models.PointField(srid=4326, geography=True)
    description = models.TextField(blank=True)
    status      = models.CharField(
                      max_length=15,
                      choices=Status.choices,
                      default=Status.ACTIVE,
                  )
    responded_at               = models.DateTimeField(null=True, blank=True)
    responded_by               = models.ForeignKey(
                                     settings.AUTH_USER_MODEL,
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name="sos_alerts_handled",
                                 )
    resolution_note            = models.TextField(blank=True)
    resolved_at                = models.DateTimeField(null=True, blank=True)
    emergency_contact_notified = models.BooleanField(default=False)

    class Meta:
        db_table        = "sira_sos_alert"
        verbose_name    = "Alerte SOS"
        verbose_name_plural = "Alertes SOS"
        ordering        = ["-created_at"]
        indexes         = [
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"SOS {self.alert_type} — {self.user} [{self.status}]"