"""
Zepto provider — verified integration strategy (2026-07).

Research findings (actual HTTP probes):
- Official public API: none
- GET https://api.zepto.co.in/api/v2/search → 404
- POST https://bff-gateway.zepto.com/user-search-service/api/v3/search cold → 429
- Playwright on https://www.zepto.com/search?query=...
  intercepts the same BFF endpoint with status 200 and product JSON
  (also verified DOM prices: Amul Salted Butter ₹63 / ₹130 / ₹310)

This provider prefers Playwright BFF interception, optional aggregators,
and returns [] so CollectorService can fall back to FakeProvider.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional
from urllib.parse import quote

from django.conf import settings

from .base import BaseProvider, ProviderProduct, extract_unit, parse_money, styled_text
from .browser import capture_matching_json, playwright_available, scrape_price_cards_from_dom
from .http import cached_json

logger = logging.getLogger(__name__)


class ZeptoProvider(BaseProvider):
    name = "Zepto"
    store_slug = "zepto"

    def __init__(self) -> None:
        self.lat = float(getattr(settings, "PROVIDER_LATITUDE", 12.9716))
        self.lon = float(getattr(settings, "PROVIDER_LONGITUDE", 77.5946))
        self.cache_ttl = int(getattr(settings, "PROVIDER_CACHE_TTL", 600))
        self.use_playwright = bool(getattr(settings, "PROVIDER_USE_PLAYWRIGHT", True))

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:zepto:search:{query.lower()}:{limit}:{self.lat}:{self.lon}"

        def loader():
            products = self._search_via_aggregator(query, limit=limit)
            if products:
                return products

            if self.use_playwright and playwright_available():
                products = self._search_via_playwright_json(query, limit=limit)
                if products:
                    return products
                products = self._search_via_playwright_dom(query, limit=limit)
                if products:
                    return products
            return []

        try:
            return cached_json(cache_key, ttl=self.cache_ttl, loader=loader) or []
        except Exception as exc:  # noqa: BLE001
            logger.warning("Zepto search error for %r: %s", query, exc)
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

    def _search_via_playwright_json(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://www.zepto.com/search?query={quote(query)}"
        payload = capture_matching_json(
            page_url=page_url,
            url_contains="user-search-service/api/v3/search",
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=12000,
            method="POST",
        )
        if not payload:
            return []
        return self._parse_bff_payload(payload, limit=limit)

    def _search_via_playwright_dom(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://www.zepto.com/search?query={quote(query)}"
        cards = scrape_price_cards_from_dom(
            page_url=page_url,
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=10000,
        )
        products = []
        for card in cards[:limit]:
            name = card["name"]
            products.append(
                ProviderProduct(
                    external_id=f"zepto-dom-{abs(hash(name)) % 10_000_000}",
                    name=name,
                    price=Decimal(str(card["price"])),
                    in_stock=True,
                    unit=card.get("unit") or extract_unit(name),
                    store=self.name,
                    product_url=page_url,
                    raw=card,
                )
            )
        if products:
            logger.info("Zepto DOM parsed %s products for %r", len(products), query)
        return products

    def _search_via_aggregator(self, query: str, *, limit: int) -> list[ProviderProduct]:
        from .aggregator import AggregatorClient

        client = AggregatorClient()
        rows = client.search(platform="Zepto", query=query, lat=self.lat, lon=self.lon)
        products: list[ProviderProduct] = []
        for row in rows[:limit]:
            try:
                products.append(
                    ProviderProduct(
                        external_id=str(row.get("id") or row.get("product_id") or row.get("pvid")),
                        name=str(row.get("name")),
                        price=Decimal(str(row.get("offer_price") or row.get("price"))),
                        mrp=Decimal(str(row["mrp"])) if row.get("mrp") is not None else None,
                        in_stock=bool(row.get("available", row.get("in_stock", True))),
                        brand=row.get("brand"),
                        unit=row.get("quantity") or row.get("unit") or row.get("packsize"),
                        image_url=(row.get("images") or [None])[0]
                        if isinstance(row.get("images"), list)
                        else row.get("image"),
                        store=self.name,
                        raw=row,
                    )
                )
            except Exception:
                continue
        return products

    def _parse_bff_payload(self, payload: Any, *, limit: int) -> list[ProviderProduct]:
        """
        Parse Zepto BFF ``user-search-service/api/v3/search`` JSON.

        Verified shape (2026-07)::

            layout[*].data.resolver.data.items[*].productResponse
              .discountedSellingPrice / .sellingPrice / .mrp   (paise, int)
              .outOfStock                                     (bool)
              .product.name / .product.brand
              .productVariant.id / .formattedPacksize / .images
        """
        products: list[ProviderProduct] = []
        seen: set[str] = set()

        for response in self._iter_product_responses(payload):
            if len(products) >= limit:
                break
            parsed = self._product_from_response(response)
            if not parsed or parsed.external_id in seen:
                continue
            seen.add(parsed.external_id)
            products.append(parsed)

        logger.info("Zepto parsed %s products from BFF JSON", len(products))
        return products[:limit]

    def _iter_product_responses(self, node: Any):
        if isinstance(node, dict):
            if isinstance(node.get("productResponse"), dict):
                yield node["productResponse"]
                # Sibling variant rollups carry their own prices/pack sizes
                rollups = node["productResponse"].get("rollUpVariantsDetails")
                if isinstance(rollups, list):
                    for rollup in rollups:
                        if isinstance(rollup, dict) and (
                            "discountedSellingPrice" in rollup or "sellingPrice" in rollup
                        ):
                            yield rollup
            elif (
                isinstance(node.get("product"), dict)
                and (
                    "discountedSellingPrice" in node
                    or "sellingPrice" in node
                    or "productVariant" in node
                )
            ):
                yield node
            for key, value in node.items():
                if key == "productResponse":
                    continue
                yield from self._iter_product_responses(value)
        elif isinstance(node, list):
            for item in node:
                yield from self._iter_product_responses(item)

    def _product_from_response(self, node: dict) -> Optional[ProviderProduct]:
        product = node.get("product") if isinstance(node.get("product"), dict) else {}
        variant = (
            node.get("productVariant")
            if isinstance(node.get("productVariant"), dict)
            else {}
        )

        name = (
            styled_text(product.get("name"))
            or styled_text(node.get("name"))
            or styled_text(variant.get("name"))
        )
        pid = (
            variant.get("id")
            or node.get("id")
            or product.get("id")
            or node.get("storeProductId")
            or node.get("objectId")
        )
        if not name or pid is None:
            return None

        # Prices live on the productResponse (or rollup), not the nested product
        price_dec = parse_money(
            node.get("discountedSellingPrice")
            if node.get("discountedSellingPrice") is not None
            else node.get("sellingPrice"),
            paise=True,
        ) or parse_money(node.get("price"), paise=True)
        if price_dec is None:
            return None

        mrp_dec = parse_money(
            node.get("mrp") if node.get("mrp") is not None else variant.get("mrp"),
            paise=True,
        )

        oos = node.get("outOfStock")
        if isinstance(oos, str):
            in_stock = oos.strip().lower() not in ("true", "1", "yes")
        elif oos is None:
            in_stock = True
        else:
            in_stock = not bool(oos)

        unit = (
            styled_text(variant.get("formattedPacksize"))
            or styled_text(variant.get("packsize"))
            or styled_text(node.get("unit"))
            or extract_unit(name)
        )

        image = None
        images = variant.get("images") or product.get("images") or node.get("images") or []
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                image = first.get("path") or first.get("url") or first.get("id")
            else:
                image = first
        image = image or node.get("image") or product.get("imageUrl") or product.get("image")

        brand = styled_text(product.get("brand")) or styled_text(node.get("brand"))

        return ProviderProduct(
            external_id=str(pid),
            name=name,
            price=price_dec,
            mrp=mrp_dec,
            in_stock=in_stock,
            brand=brand,
            unit=unit,
            image_url=str(image) if image else None,
            product_url=f"https://www.zepto.com/pn/{pid}",
            store=self.name,
            raw=node,
        )
