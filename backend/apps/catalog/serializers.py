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
        return None

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
        Simple trend vs last two history points for the cheapest store.
        Returns 'down' | 'up' | 'flat' | null.
        """
        history = list(obj.price_history.all()[:2]) if hasattr(obj, "price_history") else []
        if len(history) < 2:
            # Try related manager without slice prefetch
            history = list(
                obj.price_history.order_by("-recorded_at").values_list("price", flat=True)[:2]
            )
            if len(history) < 2:
                return None
            newest, previous = history[0], history[1]
        else:
            newest, previous = history[0].price, history[1].price

        if newest < previous:
            return "down"
        if newest > previous:
            return "up"
        return "flat"

    def get_store_count(self, obj):
        count = getattr(obj, "price_count", None)
        if count is not None:
            return count
        return obj.current_prices.count()


class CurrentPriceNestedSerializer(serializers.ModelSerializer):
    store = serializers.CharField(source="store.name")
    store_logo = serializers.URLField(source="store.logo", allow_null=True)
    store_website = serializers.URLField(source="store.website", allow_null=True)

    class Meta:
        model = CurrentPrice
        fields = [
            "store",
            "store_logo",
            "store_website",
            "price",
            "in_stock",
            "product_url",
            "last_updated",
        ]


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
        return None
