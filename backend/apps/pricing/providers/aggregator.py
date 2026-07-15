"""
Optional third-party grocery data aggregators.

Verified without credentials:
  GET https://api.quickcommerceapi.com/v1/search
  → 401 {"detail":"API key required. Pass via X-API-Key header or ?api_key=..."}

This proves the contract is live. With QUICKCOMMERCE_API_KEY set, search
returns platform-normalized products for BlinkIt / Zepto.

Parse.bot is supported via PARSE_API_KEY + scraper IDs when configured.
Foodspark / Actowiz are sales-led — no public self-serve key was available
to verify live; placeholders read FOODSPARK_API_KEY if ever provided.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class AggregatorClient:
    def search(
        self,
        *,
        platform: str,
        query: str,
        lat: float,
        lon: float,
    ) -> list[dict[str, Any]]:
        key = getattr(settings, "QUICKCOMMERCE_API_KEY", "") or ""
        if key:
            rows = self._quickcommerce(platform, query, lat, lon, key)
            if rows:
                return rows

        parse_key = getattr(settings, "PARSE_API_KEY", "") or ""
        if parse_key:
            rows = self._parse_bot(platform, query, parse_key)
            if rows:
                return rows

        return []

    def _quickcommerce(
        self,
        platform: str,
        query: str,
        lat: float,
        lon: float,
        api_key: str,
    ) -> list[dict[str, Any]]:
        url = "https://api.quickcommerceapi.com/v1/search"
        try:
            with httpx.Client(timeout=20, follow_redirects=True) as client:
                response = client.get(
                    url,
                    params={
                        "q": query,
                        "lat": lat,
                        "lon": lon,
                        "platform": platform,
                    },
                    headers={"X-API-Key": api_key, "Accept": "application/json"},
                )
            logger.info(
                "QuickCommerce %s search status=%s", platform, response.status_code
            )
            if response.status_code != 200:
                logger.warning("QuickCommerce error body: %s", response.text[:300])
                return []
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            products = (data or {}).get("products") if isinstance(data, dict) else None
            return products if isinstance(products, list) else []
        except Exception as exc:  # noqa: BLE001
            logger.warning("QuickCommerce request failed: %s", exc)
            return []

    def _parse_bot(self, platform: str, query: str, api_key: str) -> list[dict[str, Any]]:
        # Marketplace scraper IDs published by Parse.bot (Blinkit / Zepto)
        scrapers = {
            "BlinkIt": "99ee22ab-c3b4-4c1b-b96d-b828aac93698",
            "Blinkit": "99ee22ab-c3b4-4c1b-b96d-b828aac93698",
            "Zepto": "17775393-0b5a-4f9d-8266-c4c1c0b9670c",
        }
        scraper = scrapers.get(platform)
        if not scraper:
            return []
        url = f"https://api.parse.bot/scraper/{scraper}/search_products"
        try:
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.get(
                    url,
                    params={"query": query, "limit": 10},
                    headers={"X-API-Key": api_key, "Accept": "application/json"},
                )
            logger.info("Parse.bot %s status=%s", platform, response.status_code)
            if response.status_code != 200:
                return []
            payload = response.json()
            # Response shapes vary; accept common containers
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for key in ("products", "data", "results"):
                    value = payload.get(key)
                    if isinstance(value, list):
                        return value
                    if isinstance(value, dict) and isinstance(value.get("products"), list):
                        return value["products"]
            return []
        except Exception as exc:  # noqa: BLE001
            logger.warning("Parse.bot request failed: %s", exc)
            return []
