from decimal import Decimal

from apps.pricing.models import CurrentPrice, PriceHistory
from apps.notifications.services.notification_service import NotificationService

class PriceService:

    @staticmethod
    def update_price(product, store, data):

        current_price, created = CurrentPrice.objects.get_or_create(
            product=product,
            store=store,
            defaults={
                "price": Decimal(data["price"]),
                "in_stock": data["in_stock"],
            },
        )

        old_price = current_price.price
        new_price = Decimal(data["price"])

        if not created:

            if new_price < old_price:

                notification = {
                    "product_name": product.name,
                    "store_name": store.name,
                    "old_price": old_price,
                    "new_price": new_price,
                }

                NotificationService.notify(notification)

            current_price.price = new_price
            current_price.in_stock = data["in_stock"]
            current_price.save()

        PriceHistory.objects.create(
            product=product,
            store=store,
            price=new_price,
            in_stock=data["in_stock"],
        )

        return current_price