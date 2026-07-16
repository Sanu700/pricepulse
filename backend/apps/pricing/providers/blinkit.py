"""
Blinkit provider — verified integration strategy (2026-07).

Research findings (actual HTTP probes):
- Official public API: none
- Cold GET https://blinkit.com/v1/layout/search → 403/404 outside a browser
- Chromium session (Playwright) → same URL returns 200 JSON with products
- DOM also renders real ₹ prices when location is available

This provider:
1) Attempts optional aggregator keys (QuickCommerce / Parse) when configured
2) Uses Playwright to capture layout/search JSON (preferred)
3) Falls back to DOM price card parsing
4) Returns [] on total failure so CollectorService can use FakeProvider
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional
from urllib.parse import quote

from django.conf import settings

from .base import BaseProvider, ProviderProduct, extract_unit, parse_money, styled_text
from .browser import capture_matching_json, playwright_available, scrape_price_cards_from_dom
from .http import cached_json, http_get_json

logger = logging.getLogger(__name__)

BLINKIT_SEARCH_URL = "https://blinkit.com/v1/layout/search"


class BlinkitProvider(BaseProvider):
    name = "Blinkit"
    store_slug = "blinkit"

    def __init__(self) -> None:
        self.lat = float(getattr(settings, "PROVIDER_LATITUDE", 28.6139))
        self.lon = float(getattr(settings, "PROVIDER_LONGITUDE", 77.2090))
        self.cache_ttl = int(getattr(settings, "PROVIDER_CACHE_TTL", 600))
        self.use_playwright = bool(getattr(settings, "PROVIDER_USE_PLAYWRIGHT", True))

    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        cache_key = f"provider:blinkit:search:{query.lower()}:{limit}:{self.lat}:{self.lon}"

        def loader():
            # 1) Paid aggregator (if keyed)
            products = self._search_via_aggregator(query, limit=limit)
            if products:
                return products

            # 2) Cold JSON (almost always blocked — kept for completeness)
            products = self._search_cold_http(query, limit=limit)
            if products:
                return products

            # 3) Playwright JSON interception (verified success path)
            if self.use_playwright and playwright_available():
                logger.info("Blinkit: cold HTTP blocked; starting Playwright session…")
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
            logger.warning("Blinkit search error for %r: %s", query, exc)
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
                BLINKIT_SEARCH_URL,
                provider=self.store_slug,
                params={"q": query, "search_type": "type_to_search"},
                headers={
                    "lat": str(self.lat),
                    "lon": str(self.lon),
                    "app_client": "consumer_web",
                    "access_token": "null",
                },
            )
            return self._parse_layout_payload(payload, limit=limit)
        except Exception as exc:  # noqa: BLE001
            logger.info(
                "Blinkit cold HTTP blocked (expected without browser session): %s",
                exc,
            )
            return []

    def _search_via_playwright_json(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://blinkit.com/s/?q={quote(query)}"
        payload = capture_matching_json(
            page_url=page_url,
            url_contains="v1/layout/search",
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=12000,
        )
        if not payload:
            return []
        return self._parse_layout_payload(payload, limit=limit)

    def _search_via_playwright_dom(self, query: str, *, limit: int) -> list[ProviderProduct]:
        page_url = f"https://blinkit.com/s/?q={quote(query)}"
        cards = scrape_price_cards_from_dom(
            page_url=page_url,
            latitude=self.lat,
            longitude=self.lon,
            wait_ms=12000,
        )
        products: list[ProviderProduct] = []
        for idx, card in enumerate(cards[:limit]):
            name = card["name"]
            products.append(
                ProviderProduct(
                    external_id=f"blinkit-dom-{abs(hash(name)) % 10_000_000}",
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
            logger.info("Blinkit DOM parsed %s products for %r", len(products), query)
        return products

    def _search_via_aggregator(self, query: str, *, limit: int) -> list[ProviderProduct]:
        from .aggregator import AggregatorClient

        client = AggregatorClient()
        rows = client.search(platform="BlinkIt", query=query, lat=self.lat, lon=self.lon)
        products: list[ProviderProduct] = []
        for row in rows[:limit]:
            try:
                products.append(
                    ProviderProduct(
                        external_id=str(row.get("id") or row.get("product_id")),
                        name=str(row.get("name")),
                        price=Decimal(str(row.get("offer_price") or row.get("price"))),
                        mrp=Decimal(str(row["mrp"])) if row.get("mrp") is not None else None,
                        in_stock=bool(row.get("available", row.get("in_stock", True))),
                        brand=row.get("brand"),
                        unit=row.get("quantity") or row.get("unit"),
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

    def _parse_layout_payload(self, payload: Any, *, limit: int) -> list[ProviderProduct]:
        """
        Parse Blinkit ``v1/layout/search`` JSON.

        Verified shape (2026-07): ``response.snippets[*]`` with
        ``widget_type=product_card_snippet_type_2`` and fields under ``data``:
        - name / normal_price / mrp as styled ``{\"text\": \"...\"}``
        - product_id, inventory
        - atc_action.add_to_cart.cart_item → brand, unit, image_url, mrp
        """
        products: list[ProviderProduct] = []
        seen: set[str] = set()

        snippets = []
        if isinstance(payload, dict):
            response = payload.get("response") if isinstance(payload.get("response"), dict) else payload
            if isinstance(response.get("snippets"), list):
                snippets = response["snippets"]
            else:
                # Nested grid containers may wrap extra snippets
                snippets = list(self._iter_product_snippets(payload))

        for snippet in snippets:
            if len(products) >= limit:
                break
            if not isinstance(snippet, dict):
                continue
            widget = str(snippet.get("widget_type") or snippet.get("type") or "")
            data = snippet.get("data") if isinstance(snippet.get("data"), dict) else None
            if data is None:
                continue
            if widget and "product_card" not in widget and data.get("product_id") is None:
                continue

            parsed = self._product_from_snippet_data(data)
            if not parsed or parsed.external_id in seen:
                continue
            seen.add(parsed.external_id)
            products.append(parsed)

            # Emit distinct size variants listed under the card
            variants = data.get("variant_list")
            if isinstance(variants, list):
                for variant in variants:
                    if len(products) >= limit:
                        break
                    if not isinstance(variant, dict):
                        continue
                    vdata = variant.get("data") if isinstance(variant.get("data"), dict) else variant
                    if not isinstance(vdata, dict):
                        continue
                    vprod = self._product_from_snippet_data(vdata)
                    if not vprod or vprod.external_id in seen:
                        continue
                    seen.add(vprod.external_id)
                    products.append(vprod)

        logger.info("Blinkit parsed %s products from layout JSON", len(products))
        return products[:limit]

    def _iter_product_snippets(self, node: Any):
        if isinstance(node, dict):
            widget = str(node.get("widget_type") or node.get("type") or "")
            if "product_card" in widget and isinstance(node.get("data"), dict):
                yield node
            for value in node.values():
                yield from self._iter_product_snippets(value)
        elif isinstance(node, list):
            for item in node:
                yield from self._iter_product_snippets(item)

    def _product_from_snippet_data(self, data: dict) -> Optional[ProviderProduct]:
        cart = (
            ((data.get("atc_action") or {}).get("add_to_cart") or {}).get("cart_item")
            if isinstance(data.get("atc_action"), dict)
            else None
        )
        if not isinstance(cart, dict):
            cart = {}

        tracking = data.get("tracking") if isinstance(data.get("tracking"), dict) else {}
        click = tracking.get("click_map") if isinstance(tracking.get("click_map"), dict) else {}
        common = (
            tracking.get("common_attributes")
            if isinstance(tracking.get("common_attributes"), dict)
            else {}
        )

        name = (
            styled_text(data.get("name"))
            or styled_text(click.get("name"))
            or styled_text(common.get("name"))
        )
        pid = data.get("product_id") or cart.get("product_id") or click.get("product_id")
        if pid is None or not name:
            return None

        price_dec = (
            parse_money(data.get("normal_price"))
            or parse_money(data.get("selling_price"))
            or parse_money(data.get("offer_price"))
            or parse_money(cart.get("price"))
            or parse_money(cart.get("mrp"))
            or parse_money(data.get("mrp"))
        )
        if price_dec is None:
            return None

        mrp_dec = parse_money(data.get("mrp")) or parse_money(cart.get("mrp"))
        brand = (
            styled_text(data.get("brand"))
            or styled_text(data.get("brand_name"))
            or styled_text(cart.get("brand"))
            or styled_text(click.get("brand"))
        )
        unit = (
            styled_text(data.get("unit"))
            or styled_text(cart.get("unit"))
            or extract_unit(name)
        )
        image = cart.get("image_url") or data.get("image_url") or data.get("image")
        if isinstance(data.get("images"), list) and data["images"] and not image:
            first = data["images"][0]
            image = first.get("url") if isinstance(first, dict) else first

        inventory = data.get("inventory")
        if inventory is None:
            inventory = cart.get("inventory")
        in_stock = True
        if inventory is not None:
            try:
                in_stock = int(inventory) > 0
            except Exception:
                in_stock = bool(inventory)
        elif data.get("is_sold_out") is not None:
            in_stock = not bool(data.get("is_sold_out"))

        return ProviderProduct(
            external_id=str(pid).strip("'\""),
            name=name,
            price=price_dec,
            mrp=mrp_dec,
            in_stock=in_stock,
            brand=brand,
            unit=unit,
            image_url=str(image) if image else None,
            product_url=f"https://blinkit.com/prn/{pid}/prid/{pid}",
            store=self.name,
            raw=data,
        )
