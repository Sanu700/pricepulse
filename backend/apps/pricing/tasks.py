from celery import shared_task

from apps.catalog.models import Product
from apps.pricing.services.collector_services import CollectorService


@shared_task
def collect_prices():
    CollectorService.collect()
    return "Price collection completed!"


@shared_task
def refresh_products_prices(product_ids):
    """Refresh prices for a specific set of products (used by DB-first search)."""
    products = (
        Product.objects.select_related("brand", "category")
        .filter(id__in=list(product_ids))
    )
    result = CollectorService.collect(products=products)
    return f"Refreshed {len(product_ids)} products: {result}"
