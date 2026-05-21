"""
Modèles de paiement Sira.
- Payment     : paiement d'une course (flexible direct ou wallet)
- DriverPayout: reversement périodique des gains au conducteur
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel, UUIDTimestampedModel
from apps.drivers.models import DriverProfile
from apps.rides.models import Ride


class Payment(UUIDTimestampedModel):

    class Operator(models.TextChoices):
        ORANGE = "ORANGE", "Orange Money"
        MOOV   = "MOOV",   "Moov Money"
        CASH   = "CASH",   "Espèces"
        WALLET = "WALLET", "Wallet Sira"

    class Status(models.TextChoices):
        PENDING    = "PENDING",    "En attente"
        PROCESSING = "PROCESSING", "En cours"
        SUCCESS    = "SUCCESS",    "Succès"
        FAILED     = "FAILED",     "Échoué"
        REFUNDED   = "REFUNDED",   "Remboursé"

    ride                     = models.OneToOneField(
                                   Ride,
                                   on_delete=models.PROTECT,
                                   related_name="payment",
                               )
    amount                   = models.DecimalField(max_digits=10, decimal_places=2)
    operator                 = models.CharField(
                                   max_length=10,
                                   choices=Operator.choices
                               )
    status                   = models.CharField(
                                   max_length=15,
                                   choices=Status.choices,
                                   default=Status.PENDING,
                               )
    external_transaction_id  = models.CharField(
                                   max_length=100,
                                   blank=True,
                                   db_index=True
                               )
    operator_response        = models.JSONField(default=dict)
    idempotency_key          = models.CharField(max_length=100, unique=True)
    webhook_received_at      = models.DateTimeField(null=True, blank=True)
    webhook_signature_valid  = models.BooleanField(default=False)
    initiated_at             = models.DateTimeField(auto_now_add=True)
    completed_at             = models.DateTimeField(null=True, blank=True)
    attempt_count            = models.PositiveSmallIntegerField(default=0)
    last_error               = models.TextField(blank=True)
    breakdown                = models.JSONField(default=dict)

    class Meta:
        db_table        = "sira_payment"
        verbose_name    = "Paiement"
        verbose_name_plural = "Paiements"
        indexes         = [
            models.Index(fields=["status"]),
            models.Index(fields=["operator"]),
        ]

    def __str__(self):
        return f"Payment {self.id} — {self.operator} [{self.status}]"


class DriverPayout(UUIDTimestampedModel):

    class Status(models.TextChoices):
        PENDING    = "PENDING",    "En attente"
        PROCESSING = "PROCESSING", "En cours"
        SUCCESS    = "SUCCESS",    "Succès"
        FAILED     = "FAILED",     "Échoué"

    driver                  = models.ForeignKey(
                                  DriverProfile,
                                  on_delete=models.PROTECT,
                                  related_name="payouts",
                              )
    amount                  = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount       = models.DecimalField(max_digits=12, decimal_places=2)
    gross_amount            = models.DecimalField(max_digits=12, decimal_places=2)
    period_start            = models.DateField()
    period_end              = models.DateField()
    rides_count             = models.PositiveIntegerField(default=0)
    status                  = models.CharField(
                                  max_length=15,
                                  choices=Status.choices,
                                  default=Status.PENDING,
                              )
    external_transaction_id = models.CharField(max_length=100, blank=True)
    operator_response       = models.JSONField(default=dict)
    idempotency_key         = models.CharField(max_length=100, unique=True)
    initiated_at            = models.DateTimeField(null=True, blank=True)
    processed_at            = models.DateTimeField(null=True, blank=True)
    initiated_by            = models.ForeignKey(
                                  settings.AUTH_USER_MODEL,
                                  on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name="initiated_payouts",
                              )

    class Meta:
        db_table        = "sira_driver_payout"
        verbose_name    = "Reversement conducteur"
        verbose_name_plural = "Reversements conducteurs"
        ordering        = ["-period_end"]

    def __str__(self):
        return f"Payout {self.driver} — {self.period_start} / {self.period_end} [{self.status}]"