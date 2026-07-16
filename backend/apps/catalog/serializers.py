from rest_framework import serializers

from apps.pricing.models import CurrentPrice

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()
    highest_price = serializers.SerializerMethodField()
    cheapest_store = serializers.SerializerMethodField()
    savings = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    store_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "category",
            "barcode",
            "image_url",
            "description",
            "lowest_price",
            "highest_price",
            "cheapest_store",
            "savings",
            "trend",
            "store_count",
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return obj.image_url or None

    def get_lowest_price(self, obj):
        value = getattr(obj, "lowest_price", None)
        if value is not None:
            return value
        prices = list(obj.current_prices.all()) if hasattr(obj, "current_prices") else []
        return min((p.price for p in prices), default=None)

    def get_highest_price(self, obj):
        value = getattr(obj, "highest_price", None)
        if value is not None:
            return value
        prices = list(obj.current_prices.all()) if hasattr(obj, "current_prices") else []
        return max((p.price for p in prices), default=None)

    def get_cheapest_store(self, obj):
        value = getattr(obj, "cheapest_store", None)
        if value:
            return value
        prices = list(obj.current_prices.all()) if hasattr(obj, "current_prices") else []
        if not prices:
            return None
        cheapest = min(prices, key=lambda p: p.price)
        return cheapest.store.name

    def get_savings(self, obj):
        low = self.get_lowest_price(obj)
        high = self.get_highest_price(obj)
        if low is None or high is None:
            return None
        return high - low

    def get_trend(self, obj):
        """
        Compare current low vs high across stores as a cheap proxy for
        "worth comparing" without N+1 history queries on list endpoints.
        Detail pages use /stats/ and /history/ for precise trends.
        """
        low = self.get_lowest_price(obj)
        high = self.get_highest_price(obj)
        if low is None or high is None:
            return None
        spread = float(high) - float(low)
        if spread <= 0:
            return "flat"
        # Wider inter-store gap → treat as "down" opportunity (savings available)
        if spread / max(float(high), 1) >= 0.05:
            return "down"
        return "flat"

    def get_store_count(self, obj):
        count = getattr(obj, "price_count", None)
        if count is not None:
            return count
        return obj.current_prices.count()


class CurrentPriceNestedSerializer(serializers.ModelSerializer):
    store = serializers.CharField(source="store.name")
    store_logo = serializers.SerializerMethodField()
    store_website = serializers.URLField(source="store.website", allow_null=True)
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = CurrentPrice
        fields = [
            "store",
            "store_logo",
            "store_website",
            "price",
            "mrp",
            "discount_percent",
            "in_stock",
            "product_url",
            "delivery_eta",
            "last_updated",
        ]

    def get_store_logo(self, obj):
        from apps.pricing.serializers import store_logo_path

        return store_logo_path(obj.store.name)

    def get_discount_percent(self, obj):
        from apps.pricing.serializers import discount_percent

        return discount_percent(obj.mrp, obj.price)


class ProductPriceComparisonSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name")
    category = serializers.CharField(source="category.name", read_only=True)
    prices = CurrentPriceNestedSerializer(
        many=True,
        read_only=True,
        source="current_prices",
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "category",
            "image_url",
            "prices",
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return obj.image_url or None
