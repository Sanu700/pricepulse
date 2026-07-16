"""
BigBasket provider.

Research findings (2026):
- No official public API.
- Cold GET https://www.bigbasket.com/listing-svc/v2/products is guarded by
  Akamai bot protection and rejects anonymous clients.
- A real Chromium session (Playwright) on the product-search page loads the
  same listing-svc JSON, which we intercept.
- DOM price cards are parsed as a last resort.

Mirrors the Blinkit/Zepto/Instamart strategy and returns [] on total failure
so CollectorService can fall back to FakeProvider (hybrid mode).
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional
from urllib.parse import quote

from django.conf import settings

from .base import BaseProvider, ProviderProduct, build_product, extract_unit
from .browser import capture_matching_json, playwright_available, scrape_price_cards_from_dom
from .http import cached_json, http_get_json

logger = logging.getLogger(__name__)

BIGBASKET_SEARCH_URL = "https://www.bigbasket.com/listing-svc/v2/products"


class BigBasketProvider(BaseProvider):
    name = "BigBasket"
    store_slug = "bigbasket"

    def __init__(self) -> None:
        self.lat = float(getattr(settings, "PROVIDER_LATITUDE", 12.9716))
        self.lon = float(getattr(settings, "PROVIDER_LONGITUDE", 77.5946))
        self.cache_ttl = int(getattr(settings, "PROVIDER_CACHE_TTL", 300))
        self.use_playwright = bool(getattr(settings, "PROVIDER_USE_PLAYWRIGHT", True))

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:bigbasket:search:{query.lower()}:{limit}:{self.lat}:{self.lon}"

        def loader():
            products = self._search_via_aggregator(query, limit=limit)
            if products:
                return products

            products = self._search_cold_http(query, limit=limit)
            if products:
                return products

            if self.use_playwright and playwright_available():
                logger.info("BigBasket: attempting Playwright session…")
                products = self._search_via_playwright_json(query, limit=limit)
                if products:
                    return products
                products = self._search_via_playwright_dom(query, limit=limit)
                if products:
                    return products
            return []

        try:
            return self._finalize(cached_json(cache_key, ttl=self.cache_ttl, loader=loader) or [])
        except Exception as exc:  # noqa: BLE001
            logger.warning("BigBasket search error for %r: %s", query, exc)
            return []

    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        results = self.search(external_id, limit=5)
        for item in results:
            if item.external_id == str(external_id):
                return item
        return results[0] if results else None

    def get_current_price(self, external_id: str) -> Optional[Decimal]:
        product = self.get_product(external_id)
        return product.price if product else None

    def get_availability(self, external_id: str) -> Optional[bool]:
        product = self.get_product(external_id)
        return product.in_stock if product else None

    def get_store(self) -> str:
        return self.name

    # --- backends -----------------------------------------------------------------

    def _search_cold_http(self, query: str, *, limit: int) -> list[ProviderProduct]:
        try:
            payload = http_get_json(
                BIGBASKET_SEARCH_URL,
                provider=self.store_slug,
                params={"type": "ps", "slug": query, "page": 1},
                headers={"referer": "https://www.bigbasket.com/ps/"},
            )
            return self._parse_payload(payload, limit=limit)
        except Exception as exc:  # noqa: BLE001
            logger.info("BigBasket cold HTTP blocked/failed: %s", exc)
            return []

    def _search_via_playwright_json(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://www.bigbasket.com/ps/?q={quote(query)}&nc=as"
        payload = capture_matching_json(
            page_url=page_url,
            url_contains="listing-svc",
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=12000,
        )
        if not payload:
            return []
        return self._parse_payload(payload, limit=limit)

    def _search_via_playwright_dom(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://www.bigbasket.com/ps/?q={quote(query)}&nc=as"
        cards = scrape_price_cards_from_dom(
            page_url=page_url,
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=12000,
        )
        products: list[ProviderProduct] = []
        for card in cards[:limit]:
            name = card["name"]
            product = build_product(
                source=self.name,
                external_id=f"bigbasket-dom-{abs(hash(name)) % 10_000_000}",
                name=name,
                price=card["price"],
                unit=card.get("unit") or extract_unit(name),
                product_url=page_url,
                raw=card,
            )
            if product:
                products.append(product)
        if products:
            logger.info("BigBasket DOM parsed %s products for %r", len(products), query)
        return products

    def _search_via_aggregator(self, query: str, *, limit: int) -> list[ProviderProduct]:
        from .aggregator import AggregatorClient

        client = AggregatorClient()
        rows = client.search(platform="BigBasket", query=query, lat=self.lat, lon=self.lon)
        products: list[ProviderProduct] = []
        for row in rows[:limit]:
            product = build_product(
                source=self.name,
                external_id=row.get("id") or row.get("product_id"),
                name=row.get("name"),
                price=row.get("offer_price") or row.get("price"),
                mrp=row.get("mrp"),
                in_stock=row.get("available", row.get("in_stock", True)),
                brand=row.get("brand"),
                unit=row.get("quantity") or row.get("unit"),
                image_url=row.get("images") if isinstance(row.get("images"), list) else row.get("image"),
                raw=row,
            )
            if product:
                products.append(product)
        return products

    def _parse_payload(self, payload: Any, *, limit: int) -> list[ProviderProduct]:
        """Extract products from BigBasket listing-svc JSON."""
        products: list[ProviderProduct] = []
        seen: set[str] = set()

        def node_to_product(node: dict) -> Optional[ProviderProduct]:
            name = node.get("desc") or node.get("name") or node.get("display_name")
            pid = node.get("id") or node.get("sku") or node.get("product_id")
            if not name or pid is None:
                return None

            brand = node.get("brand")
            if isinstance(brand, dict):
                brand = brand.get("name")

            pricing = node.get("pricing") if isinstance(node.get("pricing"), dict) else {}
            discount = pricing.get("discount") if isinstance(pricing.get("discount"), dict) else {}
            prim = discount.get("prim_price") if isinstance(discount.get("prim_price"), dict) else {}
            price = (
                prim.get("sp")
                or discount.get("sp")
                or node.get("sp")
                or node.get("offer_price")
                or node.get("price")
            )
            mrp = discount.get("mrp") or node.get("mrp")
            if price is None:
                return None

            images = node.get("images") or []
            image = None
            if isinstance(images, list) and images:
                first = images[0]
                image = first.get("m") or first.get("l") or first.get("s") if isinstance(first, dict) else first

            unit = node.get("w") or node.get("magnitude") or node.get("unit")
            absolute_url = node.get("absolute_url") or node.get("slug")
            product_url = (
                absolute_url
                if isinstance(absolute_url, str) and absolute_url.startswith("http")
                else f"https://www.bigbasket.com/pd/{pid}/"
            )
            in_stock = not bool(node.get("out_of_stock") or node.get("is_sold_out"))

            return build_product(
                source=self.name,
                external_id=pid,
                name=name,
                price=price,
                mrp=mrp,
                in_stock=in_stock,
                brand=brand,
                unit=unit,
                image_url=image,
                product_url=product_url,
                raw=node,
            )

        def walk(node: Any) -> None:
            if len(products) >= limit:
                return
            if isinstance(node, dict):
                if ("desc" in node or "name" in node) and (
                    "pricing" in node or "sp" in node or "mrp" in node
                ):
                    product = node_to_product(node)
                    if product and product.external_id not in seen:
                        seen.add(product.external_id)
                        products.append(product)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(payload)
        logger.info("BigBasket parsed %s products from JSON", len(products))
        return products[:limit]
