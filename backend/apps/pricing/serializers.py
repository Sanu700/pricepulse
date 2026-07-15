from rest_framework import serializers

from .models import CurrentPrice, PriceHistory, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "logo", "website"]


class CurrentPriceSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    store = serializers.CharField(source="store.name", read_only=True)
    store_logo = serializers.URLField(source="store.logo", read_only=True, allow_null=True)

    class Meta:
        model = CurrentPrice
        fields = [
            "id",
            "product",
            "store",
            "store_logo",
            "price",
            "in_stock",
            "product_url",
            "last_updated",
        ]


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
