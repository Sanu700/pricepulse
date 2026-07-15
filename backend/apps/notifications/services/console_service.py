class ConsoleNotificationService:
    @staticmethod
    def send(notification: dict):
        product_name = notification["product_name"]
        store_name = notification["store_name"]
        old_price = notification["old_price"]
        new_price = notification["new_price"]
        savings = old_price - new_price

        # ASCII-only — Windows cp1252 consoles crash on emoji/₹
        lines = [
            "=" * 40,
            "PRICE DROP ALERT",
            "=" * 40,
            f"Product : {product_name}",
            f"Store   : {store_name}",
            f"Old     : Rs {old_price}",
            f"New     : Rs {new_price}",
            f"Saved   : Rs {savings}",
            "=" * 40,
        ]
        print("\n".join(lines))
