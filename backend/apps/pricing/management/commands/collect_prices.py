from django.core.management.base import BaseCommand

from apps.catalog.models import Product
from apps.pricing.collectors.fake import FakeCollector
from apps.pricing.models import Store
from apps.pricing.services import PriceService


class Command(BaseCommand):

    help = "Collect prices from all stores"

    def handle(self, *args, **kwargs):

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

        self.stdout.write(
            self.style.SUCCESS(
                "✅ Price collection completed!"
            )
        )