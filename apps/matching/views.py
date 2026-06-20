"""
Views du matching Sira.
Usage interne + administration uniquement.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser

from .models import MatchingConfiguration
from .serializers import MatchingConfigurationSerializer
from .services import activate_config


class MatchingConfigListView(APIView):
    """
    GET  /api/v1/matching/config/ — Liste des configurations
    POST /api/v1/matching/config/ — Créer une configuration (admin)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        configs = MatchingConfiguration.objects.all().order_by("-created_at")
        return Response(MatchingConfigurationSerializer(configs, many=True).data)

    def post(self, request):
        serializer = MatchingConfigurationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.save()
        return Response(
            MatchingConfigurationSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )


class MatchingConfigActivateView(APIView):
    """
    PATCH /api/v1/matching/config/{id}/activate/ — Activer une configuration
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            config = MatchingConfiguration.objects.get(pk=pk)
        except MatchingConfiguration.DoesNotExist:
            return Response(
                {"detail": "Configuration introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        config = activate_config(config)
        return Response(MatchingConfigurationSerializer(config).data)