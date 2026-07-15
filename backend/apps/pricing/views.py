from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import TruncDate
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product

from .models import CurrentPrice, PriceHistory, Store
from .serializers import (
    CurrentPriceSerializer,
    PriceHistorySerializer,
    StoreSerializer,
)


class CurrentPriceListAPIView(ListAPIView):
    queryset = CurrentPrice.objects.select_related("product", "store")
    serializer_class = CurrentPriceSerializer


class ProductCurrentPricesAPIView(ListAPIView):
    serializer_class = CurrentPriceSerializer
    pagination_class = None

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return (
            CurrentPrice.objects.filter(product_id=product_id)
            .select_related("store", "product")
            .order_by("price")
        )


class ProductPriceHistoryAPIView(ListAPIView):
    serializer_class = PriceHistorySerializer
    pagination_class = None

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        qs = (
            PriceHistory.objects.filter(product_id=product_id)
            .select_related("store")
            .order_by("recorded_at")
        )
        store = self.request.query_params.get("store")
        if store:
            qs = qs.filter(store__name__iexact=store)
        return qs


class StoreListAPIView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = None


class AnalyticsSummaryAPIView(APIView):
    """Dashboard / analytics aggregates derived from live price tables."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        products_tracked = Product.objects.count()
        stores = Store.objects.count()
        prices = CurrentPrice.objects.all()

        aggregates = prices.aggregate(
            avg_price=Avg("price"),
            min_price=Min("price"),
            max_price=Max("price"),
        )

        # Biggest drop: compare newest two history points per product+store
        drops = []
        recent_history = (
            PriceHistory.objects.select_related("product", "store")
            .order_by("-recorded_at")[:200]
        )
        seen = {}
        for row in recent_history:
            key = (row.product_id, row.store_id)
            if key not in seen:
                seen[key] = row
            elif "prev" not in seen[key].__dict__:
                prev = row
                newest = seen[key]
                if newest.price < prev.price:
                    drops.append(
                        {
                            "product_id": newest.product_id,
                            "product": newest.product.name,
                            "store": newest.store.name,
                            "from": float(prev.price),
                            "to": float(newest.price),
                            "savings": float(prev.price - newest.price),
                            "recorded_at": newest.recorded_at.isoformat(),
                        }
                    )

        drops.sort(key=lambda d: d["savings"], reverse=True)

        # Average savings across products (high - low)
        savings_total = 0
        savings_count = 0
        biggest_drop = drops[0] if drops else None

        for product in Product.objects.annotate(
            low=Min("current_prices__price"),
            high=Max("current_prices__price"),
        ):
            if product.low is not None and product.high is not None:
                savings_total += float(product.high - product.low)
                savings_count += 1

        avg_savings = round(savings_total / savings_count, 2) if savings_count else 0

        store_averages = (
            CurrentPrice.objects.values("store__name")
            .annotate(avg=Avg("price"), count=Count("id"))
            .order_by("avg")
        )

        trending = (
            Product.objects.annotate(
                low=Min("current_prices__price"),
                high=Max("current_prices__price"),
            )
            .filter(low__isnull=False)
            .order_by("low")[:8]
        )

        daily = (
            PriceHistory.objects.annotate(day=TruncDate("recorded_at"))
            .values("day")
            .annotate(avg=Avg("price"))
            .order_by("day")[:30]
        )

        return Response(
            {
                "products_tracked": products_tracked,
                "stores_compared": stores,
                "average_price": aggregates["avg_price"],
                "average_savings": avg_savings,
                "biggest_drop": biggest_drop,
                "recent_drops": drops[:8],
                "store_averages": [
                    {
                        "store": row["store__name"],
                        "avg": row["avg"],
                        "count": row["count"],
                    }
                    for row in store_averages
                ],
                "trending_products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "lowest_price": p.low,
                        "highest_price": p.high,
                        "savings": float(p.high - p.low) if p.high and p.low else 0,
                    }
                    for p in trending
                ],
                "daily_average": [
                    {"day": row["day"].isoformat() if row["day"] else None, "avg": row["avg"]}
                    for row in daily
                ],
                "cheapest_deals": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "brand": p.brand.name if p.brand_id else None,
                        "lowest_price": p.low,
                        "highest_price": p.high,
                        "savings": float(p.high - p.low) if p.high and p.low else 0,
                    }
                    for p in trending[:6]
                ],
            }
        )


class ProductStatsAPIView(APIView):
    """Per-product price statistics for the details page."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, product_id):
        history = PriceHistory.objects.filter(product_id=product_id)
        current = CurrentPrice.objects.filter(product_id=product_id)

        hist_agg = history.aggregate(
            lowest=Min("price"),
            highest=Max("price"),
            average=Avg("price"),
        )
        current_agg = current.aggregate(
            lowest=Min("price"),
            highest=Max("price"),
        )

        last_two = list(history.order_by("-recorded_at")[:2])
        last_change = None
        if len(last_two) == 2:
            newest, previous = last_two
            last_change = {
                "from": previous.price,
                "to": newest.price,
                "delta": newest.price - previous.price,
                "store": newest.store.name,
                "recorded_at": newest.recorded_at,
            }

        savings = None
        if current_agg["lowest"] is not None and current_agg["highest"] is not None:
            savings = current_agg["highest"] - current_agg["lowest"]

        return Response(
            {
                "lowest_price": hist_agg["lowest"] or current_agg["lowest"],
                "highest_price": hist_agg["highest"] or current_agg["highest"],
                "average_price": hist_agg["average"],
                "current_lowest": current_agg["lowest"],
                "current_highest": current_agg["highest"],
                "savings": savings,
                "last_change": last_change,
                "history_points": history.count(),
            }
        )
