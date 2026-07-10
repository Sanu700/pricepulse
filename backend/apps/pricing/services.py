from decimal import Decimal

from .models import CurrentPrice, PriceHistory


class PriceService:

    @staticmethod
    def update_price(product, store, data):
        """
        Creates/updates CurrentPrice.
        Always stores a PriceHistory snapshot.
        Detects price drops.
        """

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
                print(
                    f"🔥 PRICE DROP!\n"
                    f"Product : {product.name}\n"
                    f"Store   : {store.name}\n"
                    f"Old     : ₹{old_price}\n"
                    f"New     : ₹{new_price}\n"
                )

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