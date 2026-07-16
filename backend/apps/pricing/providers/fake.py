"""
Deterministic fallback provider used when live APIs are blocked.

Produces stable, product-specific prices so charts and comparisons
remain useful for demos and local development.
"""

from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Optional

from .base import BaseProvider, ProviderProduct


class FakeProvider(BaseProvider):
    name = "Fake"
    store_slug = "fake"

    def __init__(self, store_name: str = "Demo Store", base: float = 80.0, spread: float = 25.0):
        self._store_name = store_name
        self.base = base
        self.spread = spread
        self.name = store_name
        self.store_slug = store_name.lower().replace(" ", "-")

    def _price_for(self, seed: str) -> Decimal:
        digest = hashlib.md5(f"{self.store_slug}:{seed}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 1000
        price = self.base + (bucket / 1000.0) * self.spread
        # Slight store-specific bias
        return Decimal(str(round(price, 2)))

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        price = self._price_for(query)
        return [
            ProviderProduct(
                external_id=f"fake-{self.store_slug}-{hashlib.md5(query.encode()).hexdigest()[:10]}",
                name=query,
                price=price,
                in_stock=True,
                brand=None,
                product_url=None,
            )
        ][:limit]

    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        price = self._price_for(external_id)
        return ProviderProduct(
            external_id=external_id,
            name=external_id,
            price=price,
            in_stock=True,
        )

    def fetch_price_for_catalog_product(self, product) -> dict:
        price = self._price_for(product.name)
        digest = hashlib.md5(f"stock:{self.store_slug}:{product.id}".encode()).hexdigest()
        in_stock = int(digest[:2], 16) % 10 != 0
        # Deterministic MRP a little above selling price so a discount % renders
        mrp = (price * Decimal("1.12")).quantize(Decimal("0.01"))
        eta = f"{8 + int(digest[2:3], 16) % 8} mins"
        # Prefer catalog image so cards stay populated in fake/hybrid fallbacks
        image_url = getattr(product, "image_url", None)
        return {
            "price": price,
            "mrp": mrp,
            "in_stock": in_stock,
            "product_url": None,
            "image_url": image_url,
            "delivery_eta": eta,
            "external_id": f"fake-{product.id}",
            "normalized_name": product.name,
            "source": self.name,
        }
