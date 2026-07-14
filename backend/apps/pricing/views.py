from rest_framework.generics import ListAPIView

from .models import CurrentPrice
from .serializers import CurrentPriceSerializer


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