"""
Modèles cœur métier Sira.
- Ride                  : course passager OU livraison
- GPSPoint              : points GPS enregistrés pendant la course
- RecipientPositionShare: partage position destinataire (livraisons)
"""
import uuid

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.core.models import TimestampedModel, UUIDTimestampedModel
from apps.drivers.models import ClientProfile, DriverProfile, Vehicle


class Ride(UUIDTimestampedModel):

    class ServiceType(models.TextChoices):
        PASSENGER = "PASSENGER", "Course passager"
        DELIVERY  = "DELIVERY",  "Livraison"

    class Status(models.TextChoices):
        REQUESTED   = "REQUESTED",   "Demandée"
        ACCEPTED    = "ACCEPTED",    "Acceptée"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED   = "COMPLETED",   "Terminée"
        CANCELLED   = "CANCELLED",   "Annulée"

    class SelectionMethod(models.TextChoices):
        AUTO_DISPATCH    = "AUTO_DISPATCH",    "Dispatch automatique"
        MANUAL_SELECTION = "MANUAL_SELECTION", "Sélection manuelle"

    class PackageSize(models.TextChoices):
        SMALL  = "SMALL",  "Petit"
        MEDIUM = "MEDIUM", "Moyen"
        LARGE  = "LARGE",  "Grand"

    # Acteurs
    client  = models.ForeignKey(
                  ClientProfile,
                  on_delete=models.PROTECT,
                  related_name="rides",
              )
    driver  = models.ForeignKey(
                  DriverProfile,
                  on_delete=models.SET_NULL,
                  null=True, blank=True,
                  related_name="rides",
              )
    vehicle = models.ForeignKey(
                  Vehicle,
                  on_delete=models.SET_NULL,
                  null=True, blank=True,
                  related_name="rides",
              )

    # Type et statut
    service_type     = models.CharField(max_length=10, choices=ServiceType.choices)
    status           = models.CharField(
                           max_length=20,
                           choices=Status.choices,
                           default=Status.REQUESTED,
                       )
    selection_method = models.CharField(
                           max_length=20,
                           choices=SelectionMethod.choices,
                           default=SelectionMethod.AUTO_DISPATCH,
                       )

    # Localisation
    pickup_location            = gis_models.PointField(srid=4326, geography=True)
    pickup_address             = models.CharField(max_length=255, blank=True)
    dropoff_location           = gis_models.PointField(srid=4326, geography=True)
    dropoff_address            = models.CharField(max_length=255, blank=True)
    confirmed_dropoff_location = gis_models.PointField(
                                     srid=4326, geography=True,
                                     null=True, blank=True
                                 )
    actual_route               = gis_models.LineStringField(
                                     srid=4326, geography=True,
                                     null=True, blank=True
                                 )

    # Distances
    estimated_distance_m  = models.PositiveIntegerField()
    theoretical_distance_m = models.PositiveIntegerField(null=True, blank=True)
    actual_distance_m     = models.PositiveIntegerField(null=True, blank=True)

    # Prix
    estimated_price  = models.DecimalField(max_digits=10, decimal_places=2)
    final_price      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_snapshot = models.JSONField(default=dict)

    # Livraison — destinataire
    recipient_phone            = models.CharField(max_length=20, blank=True)
    recipient_name             = models.CharField(max_length=100, blank=True)
    package_description        = models.TextField(blank=True)
    package_size               = models.CharField(
                                     max_length=10,
                                     choices=PackageSize.choices,
                                     blank=True
                                 )
    package_weight_kg          = models.DecimalField(
                                     max_digits=5, decimal_places=2,
                                     null=True, blank=True
                                 )
    package_is_fragile         = models.BooleanField(default=False)
    package_value_fcfa         = models.DecimalField(
                                     max_digits=10, decimal_places=2,
                                     null=True, blank=True
                                 )
    package_photo              = models.ImageField(
                                     upload_to="rides/packages/",
                                     null=True, blank=True
                                 )
    is_urgent                  = models.BooleanField(default=False)
    forbidden_content_certified = models.BooleanField(default=False)

    # Horodatages
    requested_at     = models.DateTimeField(auto_now_add=True)
    accepted_at      = models.DateTimeField(null=True, blank=True)
    driver_arrived_at = models.DateTimeField(null=True, blank=True)
    started_at       = models.DateTimeField(null=True, blank=True)
    completed_at     = models.DateTimeField(null=True, blank=True)
    cancelled_at     = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_by     = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name="cancelled_rides",
                       )

    # Anti-fraude
    fraud_flags   = models.JSONField(default=list)
    is_flagged    = models.BooleanField(default=False)
    fraud_score   = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    # Sync offline
    synced_from_offline = models.BooleanField(default=False)
    client_local_id     = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table        = "sira_ride"
        verbose_name    = "Course"
        verbose_name_plural = "Courses"
        ordering        = ["-requested_at"]
        indexes         = [
            models.Index(fields=["status"]),
            models.Index(fields=["client"]),
            models.Index(fields=["driver"]),
        ]

    def __str__(self):
        return f"Course {self.id} — {self.service_type} [{self.status}]"

    @property
    def is_delivery(self):
        return self.service_type == self.ServiceType.DELIVERY

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED


class GPSPoint(models.Model):
    """
    Point GPS enregistré toutes les ~5 secondes.
    Volume MASSIF — pas de updated_at, immuable.
    Prévoir partitionnement par mois après 6 mois d'exploitation.
    """
    ride                = models.ForeignKey(
                              Ride,
                              on_delete=models.CASCADE,
                              related_name="gps_points",
                              db_index=True,
                          )
    location            = gis_models.PointField(
                              srid=4326, geography=True,
                              db_index=True
                          )
    accuracy_m          = models.FloatField()
    speed_kmh           = models.FloatField(null=True, blank=True)
    bearing             = models.FloatField(null=True, blank=True)
    recorded_at         = models.DateTimeField(db_index=True)
    synced_at           = models.DateTimeField(auto_now_add=True)
    is_from_offline_sync = models.BooleanField(default=False)
    is_suspect          = models.BooleanField(default=False)
    suspect_reasons     = models.JSONField(default=list)

    class Meta:
        db_table        = "sira_gps_point"
        verbose_name    = "Point GPS"
        verbose_name_plural = "Points GPS"
        ordering        = ["recorded_at"]
        indexes         = [
            models.Index(fields=["ride", "recorded_at"]),
        ]

    def __str__(self):
        return f"GPS {self.ride_id} — {self.recorded_at}"


class RecipientPositionShare(TimestampedModel):
    """
    Lien sécurisé envoyé par SMS au destinataire d'une livraison
    pour qu'il partage sa position.
    """

    class Status(models.TextChoices):
        PENDING   = "PENDING",   "En attente"
        SHARED    = "SHARED",    "Position partagée"
        EXPIRED   = "EXPIRED",   "Expiré"
        CANCELLED = "CANCELLED", "Annulé"

    ride                     = models.OneToOneField(
                                   Ride,
                                   on_delete=models.CASCADE,
                                   related_name="recipient_share",
                               )
    token                    = models.CharField(max_length=64, unique=True, db_index=True)
    recipient_phone          = models.CharField(max_length=20)
    shared_location          = gis_models.PointField(
                                   srid=4326, geography=True,
                                   null=True, blank=True
                               )
    shared_at                = models.DateTimeField(null=True, blank=True)
    shared_from_ip           = models.GenericIPAddressField(null=True, blank=True)
    shared_from_user_agent   = models.TextField(blank=True)
    status                   = models.CharField(
                                   max_length=10,
                                   choices=Status.choices,
                                   default=Status.PENDING,
                               )
    sms_sent_at              = models.DateTimeField(null=True, blank=True)
    sms_provider_message_id  = models.CharField(max_length=100, blank=True)
    expires_at               = models.DateTimeField()

    class Meta:
        db_table        = "sira_recipient_share"
        verbose_name    = "Partage position destinataire"
        verbose_name_plural = "Partages position destinataire"

    def __str__(self):
        return f"Share {self.ride_id} — {self.status}"