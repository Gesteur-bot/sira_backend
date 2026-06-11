"""
Views des profils et conducteurs Sira.
"""
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsClient, IsDriver, IsAdminUser

from .models import DriverProfile, DriverDocument
from .serializers import (
    AvailabilitySerializer,
    ClientProfileSerializer,
    DriverDocumentSerializer,
    DriverProfileCreateSerializer,
    DriverProfileSerializer,
    DriverValidationSerializer,
    LocationUpdateSerializer,
    VehicleSerializer,
)
from .services import (
    create_client_profile,
    create_driver_profile,
    update_client_profile,
    update_driver_availability,
    update_driver_location,
    validate_driver,
)


# ============================================================
# CLIENT
# ============================================================

class ClientProfileView(APIView):
    """
    GET  /api/v1/drivers/client/profile/ — Voir son profil
    POST /api/v1/drivers/client/profile/ — Créer son profil
    PUT  /api/v1/drivers/client/profile/ — Modifier son profil
    """
    permission_classes = [IsAuthenticated, IsClient]
    parser_classes     = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            profile = request.user.client_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ClientProfileSerializer(profile).data)

    def post(self, request):
        serializer = ClientProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = create_client_profile(
            request.user,
            serializer.validated_data
        )
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ClientProfileSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        serializer = ClientProfileSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = update_client_profile(
            request.user,
            serializer.validated_data
        )
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ClientProfileSerializer(result).data)


# ============================================================
# DRIVER
# ============================================================

class DriverProfileView(APIView):
    """
    GET  /api/v1/drivers/driver/profile/ — Voir son profil
    POST /api/v1/drivers/driver/profile/ — Créer son profil
    PUT  /api/v1/drivers/driver/profile/ — Modifier son profil
    """
    permission_classes = [IsAuthenticated, IsDriver]
    parser_classes     = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(DriverProfileSerializer(profile).data)

    def post(self, request):
        serializer = DriverProfileCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = create_driver_profile(
            request.user,
            serializer.validated_data
        )
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DriverProfileSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        serializer = DriverProfileCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        for field, value in serializer.validated_data.items():
            setattr(profile, field, value)
        profile.save()

        return Response(DriverProfileSerializer(profile).data)


class DriverLocationView(APIView):
    """
    PATCH /api/v1/drivers/driver/location/ — Mettre à jour position GPS
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request):
        serializer = LocationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        update_driver_location(
            profile,
            serializer.validated_data["latitude"],
            serializer.validated_data["longitude"],
        )

        return Response({"detail": "Position mise à jour."})


class DriverAvailabilityView(APIView):
    """
    PATCH /api/v1/drivers/driver/availability/ — Activer/désactiver disponibilité
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, error = update_driver_availability(
            profile,
            serializer.validated_data["is_available"],
        )
        if not success:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "detail": "Disponibilité mise à jour.",
            "is_available": serializer.validated_data["is_available"],
        })


class DriverDocumentView(APIView):
    """
    GET  /api/v1/drivers/driver/documents/ — Voir ses documents
    POST /api/v1/drivers/driver/documents/ — Soumettre un document
    """
    permission_classes = [IsAuthenticated, IsDriver]
    parser_classes     = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        documents = profile.documents.all()
        return Response(DriverDocumentSerializer(documents, many=True).data)

    def post(self, request):
        serializer = DriverDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = request.user.driver_profile
        except Exception:
            return Response(
                {"detail": "Profil introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        document = DriverDocument.objects.create(
            driver=profile,
            **serializer.validated_data,
        )

        return Response(
            DriverDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# ADMIN
# ============================================================

class AdminPendingDriversView(APIView):
    """
    GET /api/v1/drivers/admin/pending/ — Conducteurs en attente de validation
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        pending = DriverProfile.objects.filter(
            validation_status=DriverProfile.ValidationStatus.PENDING
        ).select_related("user")

        return Response(DriverProfileSerializer(pending, many=True).data)


class AdminValidateDriverView(APIView):
    """
    PATCH /api/v1/drivers/admin/{id}/validate/ — Valider ou rejeter un conducteur
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            driver_profile = DriverProfile.objects.get(pk=pk)
        except DriverProfile.DoesNotExist:
            return Response(
                {"detail": "Conducteur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DriverValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = validate_driver(
            driver_profile,
            action=serializer.validated_data["action"],
            rejection_reason=serializer.validated_data.get("rejection_reason", ""),
            validated_by=request.user,
        )

        return Response(DriverProfileSerializer(result).data)