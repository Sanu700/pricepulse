import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max, OuterRef, Prefetch, Subquery
from django.utils import timezone
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.pricing.models import CurrentPrice

from .models import Product
from .serializers import ProductPriceComparisonSerializer, ProductSerializer

logger = logging.getLogger(__name__)


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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        search_term = (request.query_params.get("search") or "").strip()
        if search_term:
            self._maybe_refresh_stale(search_term)
        return response

    def _maybe_refresh_stale(self, search_term):
        """DB-first search: if matched prices are stale, trigger an async refresh.

        A short-lived cache lock (per normalized query) prevents duplicate
        provider calls when several users search the same term at once.
        """
        mode = getattr(settings, "PROVIDER_MODE", "hybrid").lower()
        if mode == "fake":
            return

        stale_seconds = int(getattr(settings, "PROVIDER_STALE_SECONDS", 900))
        lock_key = f"search-refresh:{search_term.lower()}"
        if cache.get(lock_key):
            return

        matched = (
            self.filter_queryset(self.get_queryset())
            .annotate(last_price=Max("current_prices__last_updated"))
            .values("id", "last_price")[:20]
        )
        cutoff = timezone.now() - timedelta(seconds=stale_seconds)
        stale_ids = [
            row["id"]
            for row in matched
            if row["last_price"] is None or row["last_price"] < cutoff
        ]
        if not stale_ids:
            return

        cache.set(lock_key, True, timeout=stale_seconds)
        try:
            from apps.pricing.tasks import refresh_products_prices

            refresh_products_prices.delay(stale_ids)
        except Exception as exc:  # noqa: BLE001 — broker may be down in local dev
            logger.info("Stale refresh skipped (broker unavailable): %s", exc)
            cache.delete(lock_key)


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
