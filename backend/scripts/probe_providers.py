"""Live HTTP probes for Blinkit / Zepto / third-party grocery data sources."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import shorten

import httpx

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

probes: list[dict] = []


def probe(name: str, method: str, url: str, **kwargs) -> None:
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.request(method, url, **kwargs)
        body = response.text[:800]
        ctype = response.headers.get("content-type", "")
        probes.append(
            {
                "name": name,
                "url": str(response.url),
                "status": response.status_code,
                "content_type": ctype,
                "body_preview": body.replace("\n", " ")[:400],
                "ok_json": "json" in ctype.lower() and response.status_code < 400,
            }
        )
        print(f"[{response.status_code}] {name}")
        print(f"  URL: {response.url}")
        print(f"  CT: {ctype}")
        print(f"  BODY: {shorten(body, 200)}")
        print()
    except Exception as exc:  # noqa: BLE001
        probes.append({"name": name, "url": url, "status": "ERR", "error": str(exc)})
        print(f"[ERR] {name}: {exc}\n")


def main() -> None:
    common = {"User-Agent": UA, "Accept": "application/json, text/plain, */*"}

    probe(
        "blinkit_layout_search",
        "GET",
        "https://blinkit.com/v1/layout/search",
        params={"q": "amul butter", "search_type": "type_to_search"},
        headers={
            **common,
            "lat": "28.6139",
            "lon": "77.2090",
            "app_client": "consumer_web",
            "access_token": "null",
        },
    )
    probe(
        "blinkit_api2_search",
        "GET",
        "https://api2.grofers.com/v1/layout/search",
        params={"q": "milk"},
        headers={
            **common,
            "lat": "12.9716",
            "lon": "77.5946",
            "app_client": "consumer_android",
        },
    )
    probe(
        "blinkit_listing",
        "GET",
        "https://api.grofers.com/v1/layout/listing",
        headers={**common, "lat": "28.6139", "lon": "77.2090"},
    )
    probe(
        "blinkit_deeplink",
        "GET",
        "https://blinkit.com/v2/search/deeplink",
        params={"q": "milk"},
        headers={**common, "lat": "28.6139", "lon": "77.2090"},
    )

    probe(
        "zepto_v2_search",
        "GET",
        "https://api.zepto.co.in/api/v2/search",
        params={"query": "amul butter", "pageNumber": 0},
        headers=common,
    )
    probe(
        "zepto_bff_search",
        "POST",
        "https://bff-gateway.zepto.com/user-search-service/api/v3/search",
        headers={**common, "Content-Type": "application/json"},
        json={
            "query": "milk",
            "pageNumber": 0,
            "mode": "SHOW_ALL_RESULTS",
            "sessionId": "",
        },
    )
    probe(
        "zepto_www_search",
        "GET",
        "https://www.zeptonow.com/search",
        params={"query": "milk"},
        headers={"User-Agent": UA, "Accept": "text/html"},
    )

    probe(
        "quickcommerce_search_nokey",
        "GET",
        "https://api.quickcommerceapi.com/v1/search",
        params={
            "q": "amul",
            "lat": "12.9716",
            "lon": "77.5946",
            "platform": "BlinkIt",
        },
        headers=common,
    )

    # Legal open catalog (metadata / barcode), not store prices
    probe(
        "openfoodfacts_search",
        "GET",
        "https://world.openfoodfacts.org/cgi/search.pl",
        params={
            "search_terms": "amul butter",
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 3,
        },
        headers={"User-Agent": "PricePulse/1.0 (research; localhost)"},
    )

    out = Path(__file__).with_name("_provider_probe_results.json")
    out.write_text(json.dumps(probes, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
