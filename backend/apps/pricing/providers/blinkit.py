"""
Blinkit provider.

Blinkit does not expose a stable public documented API. Their consumer
web app talks to authenticated CDN endpoints that frequently require
geo headers, auth tokens, and change without notice.

Strategy:
1. Attempt a lightweight public search-style request (best effort).
2. On any failure (403/401/timeout/parse), return None so the collector
   can fall back to the FakeProvider simulation while keeping this
   module as the single place to plug in a working integration later.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from .base import BaseProvider, ProviderProduct
from .http import ProviderError, http_get_json, cached_json

logger = logging.getLogger(__name__)

# Public-ish discovery endpoint used by Blinkit's web client historically.
# This frequently returns 401/403 without city / auth headers — handled gracefully.
BLINKIT_SEARCH_URL = "https://blinkit.com/v1/layout/search"


class BlinkitProvider(BaseProvider):
    name = "Blinkit"
    store_slug = "blinkit"

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:blinkit:search:{query.lower()}:{limit}"

        def loader():
            try:
                payload = http_get_json(
                    BLINKIT_SEARCH_URL,
                    provider=self.store_slug,
                    params={"q": query, "search_type": "type_to_search"},
                    headers={
                        "lat": "28.6139",
                        "lon": "77.2090",
                        "app_client": "consumer_web",
                        "access_token": "null",
                    },
                )
                return self._parse_search(payload, limit=limit)
            except Exception as exc:
                logger.warning("Blinkit search failed for %r: %s", query, exc)
                raise ProviderError(str(exc)) from exc

        try:
            return cached_json(cache_key, ttl=600, loader=loader) or []
        except Exception:
            return []

    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        # No stable public product endpoint without auth — search by id as query.
        results = self.search(external_id, limit=1)
        return results[0] if results else None

    def _parse_search(self, payload, *, limit: int) -> list[ProviderProduct]:
        """
        Best-effort parser. Blinkit payloads are nested and versioned;
        we walk known shapes and ignore the rest.
        """
        products: list[ProviderProduct] = []

        def walk(node):
            if len(products) >= limit:
                return
            if isinstance(node, dict):
                # Heuristic: objects that look like product cards
                name = node.get("name") or node.get("product_name") or node.get("title")
                price = (
                    node.get("price")
                    or node.get("mrp")
                    or node.get("selling_price")
                    or (node.get("price_info") or {}).get("price")
                )
                pid = node.get("product_id") or node.get("id") or node.get("product_id_str")
                if name and price is not None and pid is not None:
                    try:
                        products.append(
                            ProviderProduct(
                                external_id=str(pid),
                                name=str(name),
                                price=Decimal(str(price)),
                                in_stock=bool(node.get("in_stock", node.get("inventory", 1))),
                                image_url=(
                                    node.get("image_url")
                                    or node.get("image")
                                    or (node.get("images") or [None])[0]
                                ),
                                brand=node.get("brand") or node.get("brand_name"),
                                product_url=f"https://blinkit.com/prn/{pid}",
                                raw=node if isinstance(node, dict) else {},
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
