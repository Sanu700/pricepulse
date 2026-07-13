class ConsoleNotificationService:

    @staticmethod
    def send(notification: dict):

        product_name = notification["product_name"]
        store_name = notification["store_name"]
        old_price = notification["old_price"]
        new_price = notification["new_price"]

        savings = old_price - new_price

        print("=" * 40)
        print("🔥 PRICE DROP ALERT")
        print("=" * 40)
        print(f"Product : {product_name}")
        print(f"Store   : {store_name}")
        print(f"Old     : ₹{old_price}")
        print(f"New     : ₹{new_price}")
        print(f"Saved   : ₹{savings}")
        print("=" * 40)