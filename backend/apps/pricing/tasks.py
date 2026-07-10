from celery import shared_task

from apps.catalog.models import Product
from apps.pricing.collectors.fake import FakeCollector
from apps.pricing.models import Store
from apps.pricing.services import PriceService


@shared_task
def collect_prices():

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

    return "Price collection completed!"