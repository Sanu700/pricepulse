from django.contrib import admin

from .models import NotificationLog, PriceAlert


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ("product", "target_price", "email", "is_active", "last_triggered_at")
    list_filter = ("is_active",)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "store_name",
        "old_price",
        "new_price",
        "channel",
        "success",
        "created_at",
    )
    list_filter = ("channel", "success")
