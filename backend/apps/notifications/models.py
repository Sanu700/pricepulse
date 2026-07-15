from django.db import models
from django.conf import settings


class PriceAlert(models.Model):
    """User-defined threshold for wishlist / price-drop alerts."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="price_alerts",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="price_alerts",
    )
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert {self.product_id} ≤ ₹{self.target_price}"


class NotificationLog(models.Model):
    """Audit trail for price-drop / wishlist notifications."""

    CHANNEL_CONSOLE = "console"
    CHANNEL_EMAIL = "email"
    CHANNEL_CHOICES = [
        (CHANNEL_CONSOLE, "Console"),
        (CHANNEL_EMAIL, "Email"),
    ]

    product_name = models.CharField(max_length=255)
    store_name = models.CharField(max_length=100)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_CONSOLE)
    recipient = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_name} @ {self.store_name}"
