"""
Views d'authentification Sira.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from .services import confirm_registration, create_otp, register_user, verify_otp


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Démarre l'inscription : crée le compte et envoie un OTP.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]
        role         = serializer.validated_data["role"]

        success, result = register_user(phone_number, role)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Code OTP envoyé. Vérifiez votre téléphone."},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    Vérifie le code OTP et active le compte.
    Retourne les tokens JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]
        code         = serializer.validated_data["code"]

        success, result = confirm_registration(phone_number, code)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        user = result
        refresh = RefreshToken.for_user(user)

        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Envoie un OTP pour connexion (pas de mot de passe).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]

        from .models import User
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": "Numéro non enregistré."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_active or user.is_suspended:
            return Response(
                {"detail": "Compte inactif ou suspendu."},
                status=status.HTTP_403_FORBIDDEN,
            )

        create_otp(phone_number)

        return Response(
            {"detail": "Code OTP envoyé. Vérifiez votre téléphone."},
            status=status.HTTP_200_OK,
        )


class LoginVerifyView(APIView):
    """
    POST /api/auth/login/verify/
    Vérifie l'OTP de connexion et retourne les tokens JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]
        code         = serializer.validated_data["code"]

        valid, result = verify_otp(phone_number, code)
        if not valid:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        from .models import User
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blackliste le refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Déconnexion réussie."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Token invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(APIView):
    """
    GET /api/auth/me/
    Retourne le profil de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)