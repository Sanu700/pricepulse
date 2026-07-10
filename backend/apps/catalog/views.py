from rest_framework.generics import ( ListAPIView, RetrieveAPIView, )
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter


from .models import Product
from .serializers import ProductSerializer, ProductPriceComparisonSerializer

class ProductListAPIView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'brand__name', 'category__name']
    ordering_fields = ['name', 'created_at', 'brand__name', 'category__name']
    ordering = ['name']
    filterset_fields = [
        "brand",
        "category",
    ]
    queryset = Product.objects.select_related(
        "brand",
        "category"
    )
    serializer_class = ProductSerializer

class ProductPriceComparisonAPIView(ListAPIView):
    queryset = Product.objects.select_related(
        "brand",
        "category",
    ).prefetch_related(
        "current_prices__store"
    )
    serializer_class = ProductPriceComparisonSerializer
    