from rest_framework import generics, permissions, serializers, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NotificationLog, PriceAlert


class AlertCreateThrottle(throttling.AnonRateThrottle):
    rate = "20/hour"


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

    def validate_email(self, value):
        # Guests may omit email; authenticated users can rely on account email.
        return value.strip() if value else ""


class PriceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    throttle_classes = [AlertCreateThrottle]

    def get_queryset(self):
        # Only return the caller's alerts (auth) or filter by product for guests.
        qs = PriceAlert.objects.select_related("product").filter(is_active=True)
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(user=user)
        product = self.request.query_params.get("product")
        if product:
            # Guests can list alerts for a product they just created — by product id only
            return qs.filter(product_id=product, user__isnull=True)[:5]
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class NotificationLogListAPIView(generics.ListAPIView):
    """Staff-only audit trail of notification deliveries."""

    permission_classes = [permissions.IsAdminUser]
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
    """Expose whether real SMTP email delivery is wired up."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        from django.conf import settings

        from .services.email_service import EmailNotificationService

        return Response(
            {
                "email_configured": EmailNotificationService.is_configured(),
                "email_backend": settings.EMAIL_BACKEND,
                "delivery": (
                    "smtp"
                    if EmailNotificationService.is_configured()
                    else "console_or_unconfigured"
                ),
            }
        )
