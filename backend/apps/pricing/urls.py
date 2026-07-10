from django.urls import path

from .views import CurrentPriceListAPIView

urlpatterns = [
    path(
        "prices/",
        CurrentPriceListAPIView.as_view(),
        name="price-list",
    ),
]