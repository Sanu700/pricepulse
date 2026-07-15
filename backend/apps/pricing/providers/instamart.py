"""
Swiggy Instamart provider.

Instamart traffic is routed through Swiggy's authenticated APIs.
Without session cookies / device tokens the endpoints reject anonymous
clients. This provider attempts a best-effort public call and returns
[] on failure so FakeProvider can fill gaps.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from .base import BaseProvider, ProviderProduct
from .http import ProviderError, http_get_json, cached_json

logger = logging.getLogger(__name__)

INSTAMART_SEARCH_URL = "https://www.swiggy.com/api/instamart/search"


class InstamartProvider(BaseProvider):
    name = "Instamart"
    store_slug = "instamart"

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:instamart:search:{query.lower()}:{limit}"

        def loader():
            try:
                payload = http_get_json(
                    INSTAMART_SEARCH_URL,
                    provider=self.store_slug,
                    params={"query": query},
                    headers={
                        "referer": "https://www.swiggy.com/instamart",
                    },
                )
                return self._parse_search(payload, limit=limit)
            except Exception as exc:
                logger.warning("Instamart search failed for %r: %s", query, exc)
                raise ProviderError(str(exc)) from exc

        try:
            return cached_json(cache_key, ttl=600, loader=loader) or []
        except Exception:
            return []

    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        results = self.search(external_id, limit=1)
        return results[0] if results else None

    def _parse_search(self, payload, *, limit: int) -> list[ProviderProduct]:
        products: list[ProviderProduct] = []

        def walk(node):
            if len(products) >= limit:
                return
            if isinstance(node, dict):
                name = node.get("display_name") or node.get("name") or node.get("title")
                price = node.get("offer_price") or node.get("price") or node.get("mrp")
                pid = node.get("product_id") or node.get("id") or node.get("sku_id")
                if name and price is not None and pid is not None:
                    try:
                        products.append(
                            ProviderProduct(
                                external_id=str(pid),
                                name=str(name),
                                price=Decimal(str(price)),
                                in_stock=bool(node.get("in_stock", True)),
                                image_url=node.get("image_url") or node.get("image"),
                                brand=node.get("brand"),
                                product_url=f"https://www.swiggy.com/instamart/item/{pid}",
                                raw=node,
                            )
                        )
                    except Exception:
                        pass
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(payload)
        return products[:limit]
