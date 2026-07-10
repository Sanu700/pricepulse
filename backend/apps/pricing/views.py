from rest_framework.generics import ListAPIView

from .models import CurrentPrice
from .serializers import CurrentPriceSerializer


class CurrentPriceListAPIView(ListAPIView):

    queryset = CurrentPrice.objects.select_related(
        "product",
        "store",
    )

    serializer_class = CurrentPriceSerializer