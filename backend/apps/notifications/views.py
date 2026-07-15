from rest_framework import generics, permissions, serializers, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NotificationLog, PriceAlert


class AlertCreateThrottle(throttling.AnonRateThrottle):
    scope = "alert_create"
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
        extra_kwargs = {
            "email": {"write_only": True, "required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        email = (attrs.get("email") or "").strip()
        attrs["email"] = email

        # Guests must provide an email; authenticated users may use account email.
        if (not user or not user.is_authenticated) and not email:
            raise serializers.ValidationError(
                {"email": "Email is required for guest price alerts."}
            )
        return attrs


class PriceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    throttle_classes = [AlertCreateThrottle]

    def get_queryset(self):
        qs = PriceAlert.objects.select_related("product").filter(is_active=True)
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(user=user)
        # Guests cannot list others' alerts (prevents email leakage).
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
