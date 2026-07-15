from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NotificationLog, PriceAlert


class PriceAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = PriceAlert
        fields = [
            "id",
            "product",
            "product_name",
            "target_price",
            "email",
            "is_active",
            "last_triggered_at",
            "created_at",
        ]
        read_only_fields = ["last_triggered_at", "created_at"]


class PriceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = PriceAlert.objects.select_related("product").filter(is_active=True)
        product = self.request.query_params.get("product")
        if product:
            qs = qs.filter(product_id=product)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class NotificationLogListAPIView(generics.ListAPIView):
    serializer_class = serializers.Serializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        logs = NotificationLog.objects.all()[:20]
        data = [
            {
                "id": log.id,
                "product_name": log.product_name,
                "store_name": log.store_name,
                "old_price": log.old_price,
                "new_price": log.new_price,
                "channel": log.channel,
                "success": log.success,
                "created_at": log.created_at,
            }
            for log in logs
        ]
        return Response(data)


class NotificationStatusAPIView(APIView):
    """Expose whether email delivery is wired up."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        from .services.email_service import EmailNotificationService

        return Response(
            {
                "email_configured": EmailNotificationService.is_configured(),
                "email_backend": __import__(
                    "django.conf", fromlist=["settings"]
                ).settings.EMAIL_BACKEND,
            }
        )
