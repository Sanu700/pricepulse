from rest_framework import serializers
from .models import CurrentPrice, PriceHistory, Store

class CurrentPriceSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    store = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = CurrentPrice
        fields = [
            'id',
            'product',
            'store',
            'price',
            'in_stock',
            'last_updated',
        ]