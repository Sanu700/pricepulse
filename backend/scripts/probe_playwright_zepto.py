"""Playwright probe: open Zepto search and capture XHR product APIs."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    from playwright.sync_api import sync_playwright

    captured: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-IN",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            geolocation={"latitude": 12.9716, "longitude": 77.5946},
            permissions=["geolocation"],
        )
        page = context.new_page()

        def on_response(response):
            url = response.url
            if any(
                x in url
                for x in (
                    "search",
                    "product",
                    "catalog",
                    "bff-gateway",
                    "user-search",
                )
            ):
                try:
                    body = response.text()[:1500]
                except Exception:
                    body = ""
                captured.append(
                    {
                        "url": url,
                        "status": response.status,
                        "content_type": response.headers.get("content-type", ""),
                        "body_preview": body.replace("\n", " ")[:400],
                    }
                )

        page.on("response", on_response)
        try:
            page.goto(
                "https://www.zeptonow.com/search?query=amul%20butter",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            page.wait_for_timeout(8000)
            title = page.title()
            text_snip = page.locator("body").inner_text()[:500]
        except Exception as exc:  # noqa: BLE001
            title = f"ERROR: {exc}"
            text_snip = ""
        browser.close()

    out = {
        "title": title,
        "text_snip": text_snip,
        "captured_count": len(captured),
        "captured": captured[:30],
    }
    path = Path(__file__).with_name("_playwright_zepto.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"title": title, "captured": len(captured), "out": str(path)}, indent=2))
    for row in captured[:10]:
        print(row["status"], row["url"][:120], row["body_preview"][:80])


if __name__ == "__main__":
    main()
