from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.health_services import HealthService


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        health_status = HealthService.check()
        if health_status["status"] == "unhealthy":
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(health_status, status=status.HTTP_200_OK)
