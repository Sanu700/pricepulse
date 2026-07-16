from rest_framework import serializers

from .models import CurrentPrice, PriceHistory, Store


def store_logo_path(store_name: str) -> str:
    """Local, self-hosted logo path (no remote CDN dependency)."""
    slug = (store_name or "").strip().lower().replace(" ", "-")
    aliases = {"swiggy-instamart": "instamart"}
    slug = aliases.get(slug, slug)
    return f"/logos/{slug}.svg"


def discount_percent(mrp, price):
    try:
        if mrp and price and float(mrp) > float(price):
            return round((float(mrp) - float(price)) / float(mrp) * 100)
    except (TypeError, ValueError):
        return None
    return None


class StoreSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ["id", "name", "logo", "website"]

    def get_logo(self, obj):
        return store_logo_path(obj.name)


class CurrentPriceSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    store = serializers.CharField(source="store.name", read_only=True)
    store_logo = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = CurrentPrice
        fields = [
            "id",
            "product",
            "store",
            "store_logo",
            "price",
            "mrp",
            "discount_percent",
            "in_stock",
            "product_url",
            "delivery_eta",
            "last_updated",
        ]

    def get_store_logo(self, obj):
        return store_logo_path(obj.store.name)

    def get_discount_percent(self, obj):
        return discount_percent(obj.mrp, obj.price)


class PriceHistorySerializer(serializers.ModelSerializer):
    store = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = PriceHistory
        fields = [
            "price",
            "store",
            "in_stock",
            "recorded_at",
        ]
