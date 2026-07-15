import logging

from django.conf import settings

from apps.catalog.models import Product
from apps.pricing.models import Store
from apps.pricing.providers import get_fallback_provider, get_provider
from apps.pricing.services.price_service import PriceService

logger = logging.getLogger(__name__)


class CollectorService:
    """
    Collect current prices for every Product × Store using the provider registry.

    PROVIDER_MODE=hybrid (default): try the real provider first; if it returns
    nothing, fall back to FakeProvider so demos and dashboards stay populated.
    """

    @staticmethod
    def collect():
        mode = getattr(settings, "PROVIDER_MODE", "hybrid").lower()
        products = Product.objects.all()
        stores = Store.objects.all()
        updated = 0
        fallbacks = 0

        for product in products:
            for store in stores:
                provider = get_provider(store.name)
                data = None

                try:
                    data = provider.fetch_price_for_catalog_product(product)
                except Exception as exc:
                    logger.warning(
                        "Provider %s failed for %s: %s",
                        store.name,
                        product.name,
                        exc,
                    )

                if not data and mode in ("hybrid", "fake"):
                    fallback = get_fallback_provider(store.name)
                    data = fallback.fetch_price_for_catalog_product(product)
                    fallbacks += 1
                    logger.info(
                        "Fallback price for %s @ %s → ₹%s",
                        product.name,
                        store.name,
                        data.get("price"),
                    )

                if not data:
                    continue

                PriceService.update_price(
                    product=product,
                    store=store,
                    data=data,
                )
                updated += 1

        logger.info(
            "Price collection finished: updated=%s fallbacks=%s mode=%s",
            updated,
            fallbacks,
            mode,
        )
        return {"updated": updated, "fallbacks": fallbacks, "mode": mode}
