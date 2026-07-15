"""
Email notification hook.

Console backend is for local demos only and does NOT count as configured
production delivery. Real SMTP activates when EMAIL_HOST is set.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailNotificationService:
    @staticmethod
    def is_configured() -> bool:
        host = getattr(settings, "EMAIL_HOST", "") or ""
        backend = getattr(settings, "EMAIL_BACKEND", "") or ""
        if "console" in backend:
            return False
        return bool(host)

    @staticmethod
    def send(notification: dict, recipient: str) -> tuple[bool, str]:
        if not recipient:
            return False, "No recipient email"

        subject = (
            f"Price drop: {notification['product_name']} now ₹{notification['new_price']}"
        )
        savings = notification["old_price"] - notification["new_price"]
        body = (
            f"Good news!\n\n"
            f"{notification['product_name']} dropped at {notification['store_name']}.\n"
            f"Was: ₹{notification['old_price']}\n"
            f"Now: ₹{notification['new_price']}\n"
            f"You save: ₹{savings}\n\n"
            f"— PricePulse\n"
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            logger.info("Email notification sent to %s", recipient)
            return True, "sent"
        except Exception as exc:
            logger.exception("Email notification failed: %s", exc)
            return False, str(exc)
