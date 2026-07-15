from django.utils import timezone

from .console_service import ConsoleNotificationService
from .email_service import EmailNotificationService


class NotificationService:
    """
    Fan-out price-drop events to console + email (when configured).

    Also persists a NotificationLog row and trips matching PriceAlert rows.
    """

    @staticmethod
    def notify(notification: dict):
        ConsoleNotificationService.send(notification)

        from apps.notifications.models import NotificationLog, PriceAlert

        NotificationLog.objects.create(
            product_name=notification["product_name"],
            store_name=notification["store_name"],
            old_price=notification["old_price"],
            new_price=notification["new_price"],
            channel=NotificationLog.CHANNEL_CONSOLE,
            success=True,
            detail="Printed to console",
        )

        product_id = notification.get("product_id")
        if product_id:
            alerts = PriceAlert.objects.select_related("user").filter(
                product_id=product_id,
                is_active=True,
                target_price__gte=notification["new_price"],
            )
            for alert in alerts:
                recipient = alert.email
                if not recipient and alert.user_id:
                    recipient = getattr(alert.user, "email", "") or ""

                if recipient and EmailNotificationService.is_configured():
                    ok, detail = EmailNotificationService.send(notification, recipient)
                    NotificationLog.objects.create(
                        product_name=notification["product_name"],
                        store_name=notification["store_name"],
                        old_price=notification["old_price"],
                        new_price=notification["new_price"],
                        channel=NotificationLog.CHANNEL_EMAIL,
                        recipient=recipient,
                        success=ok,
                        detail=detail,
                    )
                else:
                    # Architecture hook: alert matched but email not configured
                    NotificationLog.objects.create(
                        product_name=notification["product_name"],
                        store_name=notification["store_name"],
                        old_price=notification["old_price"],
                        new_price=notification["new_price"],
                        channel=NotificationLog.CHANNEL_CONSOLE,
                        recipient=recipient or "(no email)",
                        success=True,
                        detail="Alert matched — email not configured; logged only",
                    )

                alert.last_triggered_at = timezone.now()
                alert.save(update_fields=["last_triggered_at"])
