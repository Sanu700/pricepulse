"""
Zepto provider.

Zepto's storefront API is similarly gated (city / auth / anti-bot).
This module attempts a public search and gracefully returns empty
results so collectors can fall back without crashing the pipeline.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from .base import BaseProvider, ProviderProduct
from .http import ProviderError, http_get_json, cached_json

logger = logging.getLogger(__name__)

ZEPTO_SEARCH_URL = "https://api.zepto.co.in/api/v2/search"


class ZeptoProvider(BaseProvider):
    name = "Zepto"
    store_slug = "zepto"

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:zepto:search:{query.lower()}:{limit}"

        def loader():
            try:
                payload = http_get_json(
                    ZEPTO_SEARCH_URL,
                    provider=self.store_slug,
                    params={"query": query, "pageNumber": 0},
                    headers={
                        "compatible_components": "PRE_SEARCH_EXTRA_PROPERTIES",
                        "storeId": "",
                    },
                )
                return self._parse_search(payload, limit=limit)
            except Exception as exc:
                logger.warning("Zepto search failed for %r: %s", query, exc)
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
        items = []
        if isinstance(payload, dict):
            items = (
                payload.get("products")
                or payload.get("items")
                or payload.get("storeProducts")
                or []
            )
            if not items and "layout" in payload:
                items = payload.get("layout") or []

        for node in items if isinstance(items, list) else []:
            if len(products) >= limit:
                break
            if not isinstance(node, dict):
                continue
            product = node.get("product") if isinstance(node.get("product"), dict) else node
            name = product.get("name") or product.get("productName")
            price = (
                product.get("discountedSellingPrice")
                or product.get("sellingPrice")
                or product.get("mrp")
                or product.get("price")
            )
            # Zepto consumer APIs typically return integer paise.
            if isinstance(price, int):
                price = Decimal(price) / Decimal(100)
            else:
                price = Decimal(str(price))
            pid = product.get("id") or product.get("productId") or product.get("objectId")
            if not name or pid is None:
                continue
            try:
                products.append(
                    ProviderProduct(
                        external_id=str(pid),
                        name=str(name),
                        price=price,                        in_stock=bool(product.get("available", product.get("inStock", True))),
                        image_url=(
                            product.get("imageUrl")
                            or product.get("image")
                            or (product.get("images") or [None])[0]
                        ),
                        brand=product.get("brand") or product.get("brandName"),
                        product_url=f"https://www.zeptonow.com/pn/{pid}",
                        raw=product,
                    )
                )
            except Exception:
                continue
        return products
