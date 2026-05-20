"""
Modèles d'authentification Sira.
- User                : utilisateur custom (téléphone, rôle strict)
- PhoneVerificationCode : codes SMS pour vérification numéro
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.core.models import TimestampedModel


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Le numéro de téléphone est obligatoire")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_phone_verified", True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):

    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        DRIVER = "DRIVER", "Conducteur"
        ADMIN  = "ADMIN",  "Administrateur"

    phone_number       = PhoneNumberField(unique=True, region="BF")
    role               = models.CharField(max_length=10, choices=Role.choices)

    # Vérification téléphone
    is_phone_verified  = models.BooleanField(default=False)
    phone_verified_at  = models.DateTimeField(null=True, blank=True)

    # Suspension métier (différente de is_active Django)
    is_suspended       = models.BooleanField(default=False)
    suspension_reason  = models.TextField(blank=True)
    suspended_until    = models.DateTimeField(null=True, blank=True)  # NULL = permanent

    # Django
    is_active          = models.BooleanField(default=True)
    is_staff           = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = "phone_number"
    REQUIRED_FIELDS = ["role"]

    class Meta:
        db_table        = "sira_user"
        verbose_name    = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.phone_number} ({self.role})"

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_driver(self):
        return self.role == self.Role.DRIVER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class PhoneVerificationCode(TimestampedModel):
    """
    Codes OTP envoyés par SMS pour vérifier un numéro.
    Pas de FK directe vers User — l'OTP est envoyé AVANT la création du compte.
    """
    phone_number  = PhoneNumberField(region="BF", db_index=True)
    code          = models.CharField(max_length=6)
    is_used       = models.BooleanField(default=False)
    used_at       = models.DateTimeField(null=True, blank=True)
    expires_at    = models.DateTimeField()
    attempts      = models.PositiveSmallIntegerField(default=0)
    max_attempts  = models.PositiveSmallIntegerField(default=5)

    class Meta:
        db_table        = "sira_phone_otp"
        verbose_name    = "Code de vérification"
        verbose_name_plural = "Codes de vérification"

    def __str__(self):
        return f"OTP {self.phone_number}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < self.max_attempts
        )