"""
Views des courses Sira.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsClient, IsDriver, IsAdminUser

from .models import Ride, GPSPoint
from .serializers import (
    GPSPointCreateSerializer,
    OfflineRideSyncSerializer,
    RideCancelSerializer,
    RideCompleteSerializer,
    RideCreateSerializer,
    RideSerializer,
)
from .services import (
    accept_ride,
    add_gps_point,
    cancel_ride,
    complete_ride,
    create_ride,
    driver_arrived,
    start_ride,
)


class RideListCreateView(APIView):
    """
    GET  /api/v1/rides/ — Liste des courses
    POST /api/v1/rides/ — Créer une course (CLIENT)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == "CLIENT":
            try:
                rides = Ride.objects.filter(
                    client=user.client_profile
                ).order_by("-requested_at")
            except Exception:
                return Response(
                    {"detail": "Profil client introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        elif user.role == "DRIVER":
            try:
                rides = Ride.objects.filter(
                    driver=user.driver_profile
                ).order_by("-requested_at")
            except Exception:
                return Response(
                    {"detail": "Profil conducteur introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        elif user.role == "ADMIN":
            rides = Ride.objects.all().order_by("-requested_at")

        else:
            return Response(
                {"detail": "Rôle non autorisé."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(RideSerializer(rides, many=True).data)

    def post(self, request):
        if request.user.role != "CLIENT":
            return Response(
                {"detail": "Seuls les clients peuvent créer une course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RideCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ride, error = create_ride(request.user, serializer.validated_data)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_201_CREATED,
        )


class RideDetailView(APIView):
    """
    GET /api/v1/rides/{id}/ — Détail d'une course
    """
    permission_classes = [IsAuthenticated]

    def get_ride(self, pk, user):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return None

        # Vérifier accès
        if user.role == "CLIENT":
            try:
                if ride.client != user.client_profile:
                    return None
            except Exception:
                return None
        elif user.role == "DRIVER":
            try:
                if ride.driver != user.driver_profile:
                    return None
            except Exception:
                return None

        return ride

    def get(self, request, pk):
        ride = self.get_ride(pk, request.user)
        if not ride:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(RideSerializer(ride).data)


class RideAcceptView(APIView):
    """
    PATCH /api/v1/rides/{id}/accept/ — Conducteur accepte la course
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, result = accept_ride(ride, request.user)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(RideSerializer(result).data)


class RideArrivedView(APIView):
    """
    PATCH /api/v1/rides/{id}/arrived/ — Conducteur arrivé au pickup
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, result = driver_arrived(ride, request.user)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(RideSerializer(result).data)


class RideStartView(APIView):
    """
    PATCH /api/v1/rides/{id}/start/ — Démarre la course
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, result = start_ride(ride, request.user)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(RideSerializer(result).data)


class RideCompleteView(APIView):
    """
    PATCH /api/v1/rides/{id}/complete/ — Termine la course
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def patch(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RideCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = complete_ride(
            ride,
            request.user,
            serializer.validated_data["actual_distance_m"],
        )
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(RideSerializer(result).data)


class RideCancelView(APIView):
    """
    PATCH /api/v1/rides/{id}/cancel/ — Annule une course
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RideCancelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = cancel_ride(
            ride,
            request.user,
            serializer.validated_data.get("cancellation_reason", ""),
        )
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(RideSerializer(result).data)


class RideGPSPointView(APIView):
    """
    POST /api/v1/rides/{id}/gps/ — Soumettre un point GPS
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def post(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Course introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GPSPointCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, result = add_gps_point(ride, serializer.validated_data)
        if not success:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Point GPS enregistré.", "is_suspect": result.is_suspect},
            status=status.HTTP_201_CREATED,
        )


class RideAvailableView(APIView):
    """
    GET /api/v1/rides/available/ — Courses disponibles pour le conducteur
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def get(self, request):
        rides = Ride.objects.filter(
            status=Ride.Status.REQUESTED,
        ).order_by("-requested_at")

        return Response(RideSerializer(rides, many=True).data)