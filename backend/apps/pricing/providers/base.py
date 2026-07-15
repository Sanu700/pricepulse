"""
Grocery provider interface.

The rest of the application depends only on this contract — never on a
specific store's HTTP details.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class ProviderProduct:
    """Normalized product payload returned by any grocery provider."""

    external_id: str
    name: str
    price: Decimal
    in_stock: bool = True
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    raw: dict = field(default_factory=dict)


class BaseProvider(ABC):
    """Common interface implemented by Blinkit, Zepto, Instamart, etc."""

    name: str = "base"
    store_slug: str = "base"

    @abstractmethod
    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        """Search the provider catalog for products matching `query`."""

    def search_products(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        """Alias kept for callers that prefer the plural verb."""
        return self.search(query, limit=limit)

    @abstractmethod
    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        """Fetch a single product by provider-specific id."""

    def get_price(self, external_id: str) -> Optional[Decimal]:
        """Convenience helper — returns only the current price."""
        product = self.get_product(external_id)
        return product.price if product else None

    def fetch_price_for_catalog_product(self, product) -> Optional[dict]:
        """
        Resolve a PricePulse catalog Product against this provider.

        Returns a dict compatible with PriceService.update_price:
            {"price": Decimal, "in_stock": bool, "product_url": str|None}
        """
        results = self.search(product.name, limit=5)
        if not results:
            return None

        # Prefer exact / close name matches
        match = self._best_match(product.name, results)
        if not match:
            return None

        return {
            "price": match.price,
            "in_stock": match.in_stock,
            "product_url": match.product_url,
            "image_url": match.image_url,
            "external_id": match.external_id,
            "normalized_name": match.name,
        }

    @staticmethod
    def _best_match(query: str, results: list[ProviderProduct]) -> Optional[ProviderProduct]:
        q = query.lower().strip()
        for item in results:
            if item.name.lower().strip() == q:
                return item

        # Token overlap score
        q_tokens = set(q.split())

        def score(item: ProviderProduct) -> int:
            name_tokens = set(item.name.lower().split())
            return len(q_tokens & name_tokens)

        ranked = sorted(results, key=score, reverse=True)
        if ranked and score(ranked[0]) > 0:
            return ranked[0]
        return ranked[0] if ranked else None
