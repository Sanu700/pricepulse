import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    Provider fetches (network / Playwright) run concurrently on a thread pool;
    database writes happen on the main thread to keep ORM usage safe.
    """

    @staticmethod
    def _fetch(product, store, mode):
        """Pure fetch step — no DB writes, safe to run in a worker thread."""
        data = None
        provider = get_provider(store.name)
        try:
            data = provider.fetch_price_for_catalog_product(product)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Provider %s failed for %s: %s", store.name, product.name, exc)

        used_fallback = False
        if not data and mode in ("hybrid", "fake"):
            fallback = get_fallback_provider(store.name)
            data = fallback.fetch_price_for_catalog_product(product)
            used_fallback = True
        return product, store, data, used_fallback

    @staticmethod
    def collect(products=None):
        mode = getattr(settings, "PROVIDER_MODE", "hybrid").lower()
        max_workers = int(getattr(settings, "PROVIDER_MAX_WORKERS", 8))

        if products is None:
            products = Product.objects.select_related("brand", "category").all()
        stores = list(Store.objects.all())

        tasks = [(product, store) for product in products for store in stores]
        updated = 0
        fallbacks = 0

        results = []
        if max_workers > 1 and len(tasks) > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = [
                    pool.submit(CollectorService._fetch, product, store, mode)
                    for product, store in tasks
                ]
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Collector task failed: %s", exc)
        else:
            results = [
                CollectorService._fetch(product, store, mode) for product, store in tasks
            ]

        for product, store, data, used_fallback in results:
            if not data:
                continue
            if used_fallback:
                fallbacks += 1
            PriceService.update_price(product=product, store=store, data=data)
            updated += 1

        logger.info(
            "Price collection finished: updated=%s fallbacks=%s mode=%s",
            updated,
            fallbacks,
            mode,
        )
        return {"updated": updated, "fallbacks": fallbacks, "mode": mode}
