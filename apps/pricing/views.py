"""
Views tarifaires Sira.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser

from .models import PricingRule
from .serializers import PriceEstimateSerializer, PricingRuleSerializer
from .services import calculate_price, get_active_pricing_rule


class PricingRuleListView(APIView):
    """
    GET  /api/v1/pricing/rules/ — Liste des règles tarifaires actives
    POST /api/v1/pricing/rules/ — Créer une règle tarifaire (admin)
    """
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        rules = PricingRule.objects.filter(is_active=True)
        return Response(PricingRuleSerializer(rules, many=True).data)

    def post(self, request):
        serializer = PricingRuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        rule = serializer.save(created_by=request.user)
        return Response(
            PricingRuleSerializer(rule).data,
            status=status.HTTP_201_CREATED,
        )


class PriceEstimateView(APIView):
    """
    POST /api/v1/pricing/estimate/ — Estimer le prix d'une course
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PriceEstimateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        result, error = calculate_price(
            service_type  = data["service_type"],
            vehicle_type  = data["vehicle_type"],
            distance_m    = data["distance_m"],
            is_night      = data.get("is_night", False),
            package_size  = data.get("package_size"),
            is_urgent     = data.get("is_urgent", False),
        )

        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)