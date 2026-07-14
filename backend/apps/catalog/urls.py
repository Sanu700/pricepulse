from django.urls import path

from .views import (
    ProductListAPIView,
    ProductPriceComparisonAPIView,
    ProductDetailAPIView,
)

urlpatterns = [
    path(
        "products/",
        ProductListAPIView.as_view(),
        name="product-list",
    ),

    path(
        "products/<int:pk>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),

    path(
        "products/<int:pk>/prices/",
        ProductPriceComparisonAPIView.as_view(),
        name="product-price-comparison",
    ),
]