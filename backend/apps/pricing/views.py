from rest_framework.generics import ListAPIView

from .models import CurrentPrice, PriceHistory
from .serializers import (
    CurrentPriceSerializer,
    PriceHistorySerializer,
)


class CurrentPriceListAPIView(ListAPIView):

    queryset = CurrentPrice.objects.select_related(
        "product",
        "store",
    )

    serializer_class = CurrentPriceSerializer

class ProductCurrentPricesAPIView(ListAPIView):
    serializer_class = CurrentPriceSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return (
            CurrentPrice.objects
            .filter(product_id=product_id)
            .select_related("store")
            .order_by("price")
        )

class ProductPriceHistoryAPIView(ListAPIView):
    serializer_class = PriceHistorySerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return (
            PriceHistory.objects
            .filter(product_id=product_id)
            .order_by("recorded_at")
        )