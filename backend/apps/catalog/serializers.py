from rest_framework import serializers
from apps.pricing.models import CurrentPrice
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.ImageField(source='image', read_only=True, use_url=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'category',
            'barcode',
            'image_url',
            'description',
        ]


class CurrentPriceNestedSerializer(serializers.ModelSerializer):

    store = serializers.CharField(source="store.name")
    
    class Meta:
        model = CurrentPrice

        fields = [
            "store",
            "price",
            "in_stock",
            "last_updated",
        ]

class ProductPriceComparisonSerializer(serializers.ModelSerializer):

    brand = serializers.CharField(source="brand.name")
    category = serializers.CharField(source="category.name",read_only = True,)

    prices = CurrentPriceNestedSerializer(
        many=True,
        read_only=True,
        source="current_prices"
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "brand",
            "category",
            "prices",
        ]