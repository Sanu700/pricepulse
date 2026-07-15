"""
Shared Playwright helpers.

Cold HTTP to Blinkit/Zepto is blocked (403/429). A real Chromium session
can obtain the same consumer JSON the websites load — verified 2026-07.
"""

from __future__ import annotations

import logging
import re
import threading
from typing import Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_playwright_ok: Optional[bool] = None


def playwright_available() -> bool:
    global _playwright_ok
    if _playwright_ok is not None:
        return _playwright_ok

    with _lock:
        if _playwright_ok is not None:
            return _playwright_ok
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                _playwright_ok = bool(p.chromium.executable_path)
        except Exception:
            _playwright_ok = False
        return _playwright_ok


def capture_matching_json(
    *,
    page_url: str,
    url_contains: str,
    latitude: float,
    longitude: float,
    wait_ms: int = 10000,
    method: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Open page_url and return the first matching JSON response body."""
    if not playwright_available():
        return None

    from playwright.sync_api import sync_playwright

    captured: dict[str, Any] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-IN",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            geolocation={"latitude": latitude, "longitude": longitude},
            permissions=["geolocation"],
            viewport={"width": 1365, "height": 900},
        )
        page = context.new_page()

        def on_response(response) -> None:
            if captured.get("data") is not None:
                return
            if url_contains not in response.url:
                return
            # Avoid sibling endpoints that share a prefix
            if "/search/filters" in response.url or "empty_search" in response.url:
                return
            if response.status != 200:
                return
            if method and response.request.method.upper() != method.upper():
                return
            try:
                captured["data"] = response.json()
                captured["url"] = response.url
            except Exception:
                return

        page.on("response", on_response)
        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(wait_ms)
            if captured.get("data") is None:
                page.wait_for_timeout(5000)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Playwright failed for %s: %s", page_url, exc)
        finally:
            context.close()
            browser.close()

    if "data" not in captured:
        logger.warning("No JSON matched %r from %s", url_contains, page_url)
        return None
    logger.info("Captured %s via Playwright (%s)", url_contains, captured.get("url"))
    return captured["data"]


def scrape_price_cards_from_dom(
    *,
    page_url: str,
    latitude: float,
    longitude: float,
    wait_ms: int = 10000,
) -> list[dict[str, Any]]:
    """
    Fallback: parse visible product name + ₹ price pairs from the rendered page.
    Used when JSON interception fails but the UI still renders listings
    (verified on Blinkit).
    """
    if not playwright_available():
        return []

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-IN",
            geolocation={"latitude": latitude, "longitude": longitude},
            permissions=["geolocation"],
            viewport={"width": 1365, "height": 900},
        )
        page = context.new_page()
        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(wait_ms)
            text = page.locator("body").inner_text()
        except Exception as exc:  # noqa: BLE001
            logger.warning("DOM scrape failed for %s: %s", page_url, exc)
            text = ""
        finally:
            context.close()
            browser.close()

    return _parse_dom_products(text)


_PRICE_RE = re.compile(r"₹\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)")


def _parse_dom_products(text: str) -> list[dict[str, Any]]:
    """Heuristic splitter for grocery SPA text dumps."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    products: list[dict[str, Any]] = []
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        # Skip chrome UI
        if line.lower() in {"add", "login", "cart", "search", "filters"}:
            i += 1
            continue
        # Look ahead for a price nearby
        window = " ".join(lines[i : i + 6])
        prices = _PRICE_RE.findall(window)
        if prices and len(line) > 3 and not line.startswith("₹") and not line.isdigit():
            # Prefer the offer price (first ₹ after discounts often MRP then offer —
            # Blinkit shows MRP struck then offer; DOM text often offers MRP then sale.
            # Use the *last* small price in window if multiple, else first.
            nums = [float(p.replace(",", "")) for p in prices]
            price = min(nums) if nums else None
            if price and price > 1:
                unit = None
                for neighbor in lines[i + 1 : i + 4]:
                    if re.search(r"\b(\d+\s?(g|kg|ml|l|pack|pcs)\b)", neighbor, re.I):
                        unit = neighbor
                        break
                products.append(
                    {
                        "name": line[:180],
                        "price": price,
                        "unit": unit,
                        "source": "dom",
                    }
                )
                i += 3
                continue
        i += 1

    # Deduplicate by name
    seen = set()
    unique = []
    for item in products:
        key = item["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def search_url(template: str, query: str) -> str:
    return template.format(q=quote(query))
