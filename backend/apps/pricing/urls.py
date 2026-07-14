from django.urls import path

from .views import CurrentPriceListAPIView, ProductCurrentPricesAPIView

urlpatterns = [
    path(
        "prices/",
        CurrentPriceListAPIView.as_view(),
        name="price-list",
    ),
    path(
        "prices/product/<int:product_id>/",
        ProductCurrentPricesAPIView.as_view(),
        name="product-price-list",
    ),
]