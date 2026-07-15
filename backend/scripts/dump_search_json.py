"""Dump full Blinkit + Zepto search JSON via Playwright wait_for_response."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def dump_blinkit() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            locale="en-IN",
            geolocation={"latitude": 28.6139, "longitude": 77.2090},
            permissions=["geolocation"],
        )
        page = ctx.new_page()
        with page.expect_response(
            lambda r: "v1/layout/search" in r.url
            and r.status == 200
            and "offset=" not in r.url,
            timeout=60000,
        ) as resp_info:
            page.goto(
                "https://blinkit.com/s/?q=tata%20salt",
                wait_until="domcontentloaded",
                timeout=60000,
            )
        response = resp_info.value
        data = response.json()
        Path("scripts/_blinkit_search_sample.json").write_text(
            json.dumps({"url": response.url, "data": data}, indent=2)[:200000],
            encoding="utf-8",
        )
        print("blinkit saved", response.url, "keys", list(data)[:10])
        browser.close()


def dump_zepto() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            locale="en-IN",
            geolocation={"latitude": 12.9716, "longitude": 77.5946},
            permissions=["geolocation"],
        )
        page = ctx.new_page()
        with page.expect_response(
            lambda r: "user-search-service/api/v3/search" in r.url
            and r.request.method == "POST"
            and r.status == 200,
            timeout=60000,
        ) as resp_info:
            page.goto(
                "https://www.zepto.com/search?query=tata%20salt",
                wait_until="domcontentloaded",
                timeout=60000,
            )
        response = resp_info.value
        data = response.json()
        Path("scripts/_zepto_search_sample.json").write_text(
            json.dumps({"url": response.url, "data": data}, indent=2)[:200000],
            encoding="utf-8",
        )
        print("zepto saved", response.url, "keys", list(data)[:10])
        browser.close()


if __name__ == "__main__":
    dump_blinkit()
    dump_zepto()
