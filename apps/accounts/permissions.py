"""
Permissions custom Sira.
Utilisées dans toutes les views pour restreindre l'accès selon le rôle.
"""
from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """Autorise uniquement les utilisateurs avec role=CLIENT."""
    message = "Accès réservé aux clients."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "CLIENT"
        )


class IsDriver(BasePermission):
    """Autorise uniquement les utilisateurs avec role=DRIVER."""
    message = "Accès réservé aux conducteurs."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "DRIVER"
        )


class IsAdminUser(BasePermission):
    """Autorise uniquement les utilisateurs avec role=ADMIN."""
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsDriverValidated(BasePermission):
    """Autorise uniquement les conducteurs validés par l'admin."""
    message = "Votre compte conducteur n'est pas encore validé."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "DRIVER"
            and hasattr(request.user, "driver_profile")
            and request.user.driver_profile.is_validated
        )


class IsNotSuspended(BasePermission):
    """Refuse l'accès aux utilisateurs suspendus."""
    message = "Votre compte est suspendu."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_suspended
        )