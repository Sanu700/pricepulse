from django.urls import path

from .views import (
    AnalyticsSummaryAPIView,
    CurrentPriceListAPIView,
    ProductCurrentPricesAPIView,
    ProductPriceHistoryAPIView,
    ProductStatsAPIView,
    StoreListAPIView,
)

urlpatterns = [
    path("prices/", CurrentPriceListAPIView.as_view(), name="price-list"),
    path(
        "prices/product/<int:product_id>/",
        ProductCurrentPricesAPIView.as_view(),
        name="product-price-list",
    ),
    path(
        "products/<int:product_id>/history/",
        ProductPriceHistoryAPIView.as_view(),
        name="product-history",
    ),
    path(
        "products/<int:product_id>/stats/",
        ProductStatsAPIView.as_view(),
        name="product-stats",
    ),
    path("stores/", StoreListAPIView.as_view(), name="store-list"),
    path("analytics/summary/", AnalyticsSummaryAPIView.as_view(), name="analytics-summary"),
]
