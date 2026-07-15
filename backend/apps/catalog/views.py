from django.db.models import Count, OuterRef, Prefetch, Subquery
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.pricing.models import CurrentPrice

from .models import Product
from .serializers import ProductPriceComparisonSerializer, ProductSerializer


def _product_queryset():
    lowest = (
        CurrentPrice.objects.filter(product=OuterRef("pk"))
        .order_by("price")
        .values("price")[:1]
    )
    highest = (
        CurrentPrice.objects.filter(product=OuterRef("pk"))
        .order_by("-price")
        .values("price")[:1]
    )
    cheapest_store = (
        CurrentPrice.objects.filter(product=OuterRef("pk"))
        .order_by("price")
        .values("store__name")[:1]
    )

    return (
        Product.objects.select_related("brand", "category")
        .prefetch_related(
            Prefetch(
                "current_prices",
                queryset=CurrentPrice.objects.select_related("store").order_by("price"),
            )
        )
        .annotate(
            lowest_price=Subquery(lowest),
            highest_price=Subquery(highest),
            cheapest_store=Subquery(cheapest_store),
            price_count=Count("current_prices"),
        )
    )


class ProductListAPIView(ListAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "brand__name", "category__name"]
    ordering_fields = [
        "name",
        "created_at",
        "brand__name",
        "category__name",
        "lowest_price",
    ]
    ordering = ["name"]
    filterset_fields = ["brand", "category"]
    queryset = _product_queryset()
    serializer_class = ProductSerializer


class ProductPriceComparisonAPIView(RetrieveAPIView):
    """Return a single product with nested store prices (ordered cheapest first)."""

    queryset = Product.objects.select_related("brand", "category").prefetch_related(
        Prefetch(
            "current_prices",
            queryset=CurrentPrice.objects.select_related("store").order_by("price"),
        )
    )
    serializer_class = ProductPriceComparisonSerializer


class ProductDetailAPIView(RetrieveAPIView):
    queryset = _product_queryset()
    serializer_class = ProductSerializer
