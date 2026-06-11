"""
Services d'authentification Sira.
Logique métier isolée des views :
- Génération et envoi d'OTP
- Validation d'OTP
- Création de compte
"""
import random
import string
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import User, PhoneVerificationCode


def generate_otp_code(length=6):
    """Génère un code numérique aléatoire à 6 chiffres."""
    return "".join(random.choices(string.digits, k=length))


def send_otp_sms(phone_number, code):
    """
    Envoie le code OTP par SMS.
    En dev : affiche dans la console.
    En prod : appel API SMS (Orange, etc.)
    """
    print(f"[SMS OTP] {phone_number} → Code : {code}")
    # TODO : intégrer l'API SMS en production
    return True


def create_otp(phone_number):
    """
    Crée un nouveau code OTP pour un numéro de téléphone.
    Invalide les anciens codes non utilisés.
    """
    # Invalider les anciens codes
    PhoneVerificationCode.objects.filter(
        phone_number=phone_number,
        is_used=False,
    ).update(is_used=True)

    # Générer nouveau code
    code = generate_otp_code()
    expires_at = timezone.now() + timedelta(
        minutes=settings.SIRA_OTP_VALIDITY_MINUTES
    )

    otp = PhoneVerificationCode.objects.create(
        phone_number=phone_number,
        code=code,
        expires_at=expires_at,
    )

    # Envoyer SMS
    send_otp_sms(phone_number, code)

    return otp


def verify_otp(phone_number, code):
    """
    Vérifie un code OTP.
    Retourne (True, otp) si valide, (False, message_erreur) sinon.
    """
    try:
        otp = PhoneVerificationCode.objects.filter(
            phone_number=phone_number,
            is_used=False,
        ).latest("created_at")
    except PhoneVerificationCode.DoesNotExist:
        return False, "Aucun code trouvé pour ce numéro."

    # Incrémenter les tentatives
    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if not otp.is_valid:
        if otp.is_expired:
            return False, "Code expiré. Demandez un nouveau code."
        if otp.attempts >= otp.max_attempts:
            return False, "Trop de tentatives. Demandez un nouveau code."
        return False, "Code invalide."

    if otp.code != code:
        return False, "Code incorrect."

    # Marquer comme utilisé
    otp.is_used = True
    otp.used_at = timezone.now()
    otp.save(update_fields=["is_used", "used_at"])

    return True, otp


def register_user(phone_number, role):
    """
    Démarre l'inscription : crée ou récupère le User,
    envoie un OTP de vérification.
    """
    # Vérifier si le numéro existe déjà
    if User.objects.filter(phone_number=phone_number).exists():
        return False, "Ce numéro est déjà enregistré."

    # Créer le user sans mot de passe (sera défini après OTP)
    user = User.objects.create_user(
        phone_number=phone_number,
        role=role,
        is_active=False,  # Inactif jusqu'à vérification OTP
    )

    # Envoyer OTP
    create_otp(phone_number)

    return True, user


def confirm_registration(phone_number, code):
    """
    Confirme l'inscription après vérification OTP.
    Active le compte et marque le téléphone comme vérifié.
    """
    valid, result = verify_otp(phone_number, code)
    if not valid:
        return False, result

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return False, "Utilisateur introuvable."

    user.is_active = True
    user.is_phone_verified = True
    user.phone_verified_at = timezone.now()
    user.save(update_fields=["is_active", "is_phone_verified", "phone_verified_at"])

    return True, user