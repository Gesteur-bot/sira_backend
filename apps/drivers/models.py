"""
Modèles métier des profils et conducteurs Sira.
- ClientProfile  : profil client
- DriverProfile  : profil conducteur
- AdminProfile   : profil administrateur
- Vehicle        : véhicules
- DriverDocument : documents administratifs
- DriverScore    : historique scores
"""
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.core.models import TimestampedModel


class ClientProfile(TimestampedModel):

    class PreferredPayment(models.TextChoices):
        ORANGE = "ORANGE", "Orange Money"
        MOOV   = "MOOV",   "Moov Money"
        CASH   = "CASH",   "Espèces"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
        limit_choices_to={"role": "CLIENT"},
    )
    first_name               = models.CharField(max_length=100)
    last_name                = models.CharField(max_length=100)
    photo                    = models.ImageField(
                                   upload_to="clients/photos/",
                                   null=True, blank=True
                               )
    email                    = models.EmailField(blank=True)
    preferred_payment_method = models.CharField(
                                   max_length=20,
                                   choices=PreferredPayment.choices,
                                   blank=True
                               )
    default_pickup_location  = gis_models.PointField(
                                   null=True, blank=True, srid=4326,
                                   geography=True
                               )
    total_rides              = models.PositiveIntegerField(default=0)
    client_score             = models.DecimalField(
                                   max_digits=5, decimal_places=2,
                                   default=100.00
                               )

    class Meta:
        db_table        = "sira_client_profile"
        verbose_name    = "Profil client"
        verbose_name_plural = "Profils clients"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class DriverProfile(TimestampedModel):

    class ValidationStatus(models.TextChoices):
        PENDING   = "PENDING",   "En attente"
        APPROVED  = "APPROVED",  "Approuvé"
        REJECTED  = "REJECTED",  "Rejeté"
        SUSPENDED = "SUSPENDED", "Suspendu"

    class MobileOperator(models.TextChoices):
        ORANGE = "ORANGE", "Orange Money"
        MOOV   = "MOOV",   "Moov Money"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
        limit_choices_to={"role": "DRIVER"},
    )
    first_name                 = models.CharField(max_length=100)
    last_name                  = models.CharField(max_length=100)
    photo                      = models.ImageField(upload_to="drivers/photos/")
    mobile_money_number        = models.CharField(max_length=20)
    mobile_money_operator      = models.CharField(
                                     max_length=10,
                                     choices=MobileOperator.choices
                                 )
    # Validation
    validation_status          = models.CharField(
                                     max_length=15,
                                     choices=ValidationStatus.choices,
                                     default=ValidationStatus.PENDING,
                                 )
    validated_at               = models.DateTimeField(null=True, blank=True)
    validated_by               = models.ForeignKey(
                                     settings.AUTH_USER_MODEL,
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name="validated_drivers",
                                 )
    rejection_reason           = models.TextField(blank=True)

    # Position et disponibilité
    is_available               = models.BooleanField(default=False)
    current_location           = gis_models.PointField(
                                     null=True, blank=True,
                                     srid=4326, geography=True,
                                     db_index=True
                                 )
    last_location_update       = models.DateTimeField(null=True, blank=True)

    # Score
    current_score              = models.DecimalField(
                                     max_digits=5, decimal_places=2,
                                     default=70.00, db_index=True
                                 )
    last_score_update          = models.DateTimeField(null=True, blank=True)
    is_in_matching_suspension  = models.BooleanField(default=False)

    # Stats
    last_ride_completed_at     = models.DateTimeField(null=True, blank=True)
    total_rides                = models.PositiveIntegerField(default=0)
    total_completed_rides      = models.PositiveIntegerField(default=0)
    total_cancelled_rides      = models.PositiveIntegerField(default=0)
    average_rating             = models.DecimalField(
                                     max_digits=3, decimal_places=2,
                                     default=0
                                 )
    total_ratings              = models.PositiveIntegerField(default=0)

    # Direction préférée (future Voie C)
    preferred_direction        = gis_models.PointField(
                                     null=True, blank=True,
                                     srid=4326, geography=True
                                 )
    preferred_direction_name   = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table        = "sira_driver_profile"
        verbose_name    = "Profil conducteur"
        verbose_name_plural = "Profils conducteurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name} [{self.validation_status}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_validated(self):
        return self.validation_status == self.ValidationStatus.APPROVED


class AdminProfile(TimestampedModel):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile",
        limit_choices_to={"role": "ADMIN"},
    )
    first_name         = models.CharField(max_length=100)
    last_name          = models.CharField(max_length=100)
    email              = models.EmailField()
    position           = models.CharField(max_length=100, blank=True)
    department         = models.CharField(max_length=50, blank=True)
    permissions_scope  = models.JSONField(default=dict)

    class Meta:
        db_table        = "sira_admin_profile"
        verbose_name    = "Profil administrateur"
        verbose_name_plural = "Profils administrateurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"


class Vehicle(TimestampedModel):

    class VehicleType(models.TextChoices):
        MOTO_2W = "MOTO_2W", "Moto 2 roues"
        MOTO_3W = "MOTO_3W", "Moto 3 roues (tricycle)"
        # CAR_4W = "CAR_4W", "Voiture 4 roues (V2)"

    class CargoCapacity(models.TextChoices):
        SMALL  = "SMALL",  "Petit"
        MEDIUM = "MEDIUM", "Moyen"
        LARGE  = "LARGE",  "Grand"

    driver              = models.ForeignKey(
                              DriverProfile,
                              on_delete=models.CASCADE,
                              related_name="vehicles",
                          )
    vehicle_type        = models.CharField(max_length=10, choices=VehicleType.choices)
    license_plate       = models.CharField(max_length=20, unique=True)
    brand               = models.CharField(max_length=50)
    model               = models.CharField(max_length=50)
    color               = models.CharField(max_length=30)
    year                = models.PositiveSmallIntegerField(null=True, blank=True)
    passenger_capacity  = models.PositiveSmallIntegerField(default=1)
    cargo_capacity      = models.CharField(
                              max_length=10,
                              choices=CargoCapacity.choices,
                              default=CargoCapacity.SMALL
                          )
    required_license_type = models.CharField(max_length=2, default="A")
    photo               = models.ImageField(upload_to="vehicles/photos/")
    is_active           = models.BooleanField(default=True)

    class Meta:
        db_table        = "sira_vehicle"
        verbose_name    = "Véhicule"
        verbose_name_plural = "Véhicules"

    def __str__(self):
        return f"{self.license_plate} ({self.brand} {self.model}) — {self.driver}"


class DriverDocument(TimestampedModel):

    class DocumentType(models.TextChoices):
        ID_CARD              = "ID_CARD",              "Carte Nationale d'Identité"
        DRIVER_LICENSE       = "DRIVER_LICENSE",       "Permis de conduire"
        VEHICLE_REGISTRATION = "VEHICLE_REGISTRATION", "Carte grise"
        INSURANCE            = "INSURANCE",            "Assurance"
        DRIVER_PHOTO         = "DRIVER_PHOTO",         "Photo conducteur"

    class VerificationStatus(models.TextChoices):
        PENDING  = "PENDING",  "En attente"
        APPROVED = "APPROVED", "Approuvé"
        REJECTED = "REJECTED", "Rejeté"
        EXPIRED  = "EXPIRED",  "Expiré"

    driver              = models.ForeignKey(
                              DriverProfile,
                              on_delete=models.CASCADE,
                              related_name="documents",
                          )
    vehicle             = models.ForeignKey(
                              Vehicle,
                              on_delete=models.SET_NULL,
                              null=True, blank=True,
                              related_name="documents",
                          )
    document_type       = models.CharField(max_length=25, choices=DocumentType.choices)
    file                = models.ImageField(upload_to="drivers/documents/")
    issued_date         = models.DateField(null=True, blank=True)
    expiry_date         = models.DateField(null=True, blank=True, db_index=True)
    verification_status = models.CharField(
                              max_length=10,
                              choices=VerificationStatus.choices,
                              default=VerificationStatus.PENDING,
                          )
    verified_at         = models.DateTimeField(null=True, blank=True)
    verified_by         = models.ForeignKey(
                              settings.AUTH_USER_MODEL,
                              on_delete=models.SET_NULL,
                              null=True, blank=True,
                              related_name="verified_documents",
                          )
    rejection_reason    = models.TextField(blank=True)

    class Meta:
        db_table        = "sira_driver_document"
        verbose_name    = "Document conducteur"
        verbose_name_plural = "Documents conducteurs"

    def __str__(self):
        return f"{self.driver} — {self.document_type} [{self.verification_status}]"


class DriverScore(models.Model):
    """
    Historique des scores. Recalculé quotidiennement par tâche Celery.
    Pas de updated_at car immuable (on crée, on ne modifie jamais).
    """
    driver                   = models.ForeignKey(
                                   DriverProfile,
                                   on_delete=models.CASCADE,
                                   related_name="score_history",
                               )
    overall_score            = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
    rating_score             = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
    acceptance_score         = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
    completion_score         = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
    seniority_score          = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    incident_score           = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    computed_at              = models.DateTimeField(auto_now_add=True)
    computation_period_start = models.DateField()
    computation_period_end   = models.DateField()
    rides_evaluated_count    = models.PositiveIntegerField(default=0)

    class Meta:
        db_table        = "sira_driver_score"
        verbose_name    = "Score conducteur"
        verbose_name_plural = "Scores conducteurs"
        ordering        = ["-computed_at"]

    def __str__(self):
        return f"{self.driver} — {self.overall_score} ({self.computed_at.date()})"