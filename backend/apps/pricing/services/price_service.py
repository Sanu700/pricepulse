from decimal import Decimal

from apps.notifications.services.notification_service import NotificationService
from apps.pricing.models import CurrentPrice, PriceHistory


class PriceService:
    @staticmethod
    def update_price(product, store, data):
        new_price = Decimal(str(data["price"]))
        in_stock = bool(data.get("in_stock", True))
        product_url = data.get("product_url")
        image_url = data.get("image_url")

        current_price, created = CurrentPrice.objects.get_or_create(
            product=product,
            store=store,
            defaults={
                "price": new_price,
                "in_stock": in_stock,
                "product_url": product_url,
            },
        )

        old_price = current_price.price

        if not created:
            if new_price < old_price:
                NotificationService.notify(
                    {
                        "product_name": product.name,
                        "product_id": product.id,
                        "store_name": store.name,
                        "old_price": old_price,
                        "new_price": new_price,
                    }
                )

            current_price.price = new_price
            current_price.in_stock = in_stock
            if product_url:
                current_price.product_url = product_url
            current_price.save(update_fields=["price", "in_stock", "product_url", "last_updated"])

        # Persist provider image onto the catalog product when missing
        if image_url and not product.image_url and not product.image:
            product.image_url = str(image_url)[:500]
            product.save(update_fields=["image_url", "updated_at"])

        # Avoid flooding history with identical consecutive readings
        last = (
            PriceHistory.objects.filter(product=product, store=store)
            .order_by("-recorded_at")
            .first()
        )
        if (
            last is None
            or last.price != new_price
            or last.in_stock != in_stock
            or created
        ):
            PriceHistory.objects.create(
                product=product,
                store=store,
                price=new_price,
                in_stock=in_stock,
            )

        return current_price
