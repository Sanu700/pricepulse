from apps.catalog.models import Product
from apps.pricing.collectors.fake import FakeCollector
from apps.pricing.models import Store

from apps.pricing.services.price_service import PriceService

class CollectorService:
    @staticmethod
    def collect():
        collector = FakeCollector()

        products = Product.objects.all()
        stores = Store.objects.all()

        for product in products:
            for store in stores:
                data = collector.fetch_price(product)

                PriceService.update_price(
                    product=product,
                    store=store,
                    data=data,
                )