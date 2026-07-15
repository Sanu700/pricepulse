"""
Verify live Blinkit / Zepto providers end-to-end.

Run:
  python scripts/verify_live_providers.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("PROVIDER_MODE", "live")
os.environ.setdefault("PROVIDER_USE_PLAYWRIGHT", "True")

import django

django.setup()

from django.core.cache import cache  # noqa: E402

from apps.catalog.models import Product  # noqa: E402
from apps.pricing.models import CurrentPrice, PriceHistory, Store  # noqa: E402
from apps.pricing.providers import BlinkitProvider, ZeptoProvider  # noqa: E402
from apps.pricing.services.price_service import PriceService  # noqa: E402


def dump_products(label: str, products) -> dict:
    rows = [
        {
            "id": p.external_id,
            "name": p.name,
            "price": str(p.price),
            "unit": p.unit,
            "brand": p.brand,
            "in_stock": p.in_stock,
        }
        for p in products[:8]
    ]
    print(f"\n=== {label} ===")
    print(f"count={len(products)}")
    for row in rows:
        # ASCII-safe for Windows consoles (cp1252)
        print(f"  Rs{row['price']:>8}  {row['name'][:60]}")
    return {"count": len(products), "sample": rows}


def main() -> None:
    query = "amul butter"
    report: dict = {"query": query, "providers": {}}

    # Avoid stale empty/partial cache from earlier parser bugs
    try:
        cache.clear()
    except Exception:
        pass

    blinkit = BlinkitProvider()
    zepto = ZeptoProvider()

    print("Interface check:", blinkit.get_store(), zepto.get_store())
    assert hasattr(blinkit, "search")
    assert hasattr(blinkit, "get_product")
    assert hasattr(blinkit, "get_current_price")
    assert hasattr(blinkit, "get_availability")
    assert hasattr(blinkit, "get_store")

    b_products = blinkit.search(query, limit=8)
    z_products = zepto.search(query, limit=8)
    report["providers"]["blinkit"] = dump_products("Blinkit", b_products)
    report["providers"]["zepto"] = dump_products("Zepto", z_products)

    catalog = (
        Product.objects.filter(name__icontains="Amul")
        .filter(name__icontains="Butter")
        .first()
        or Product.objects.filter(name__icontains="Amul Butter").first()
    )
    stored = {"blinkit": 0, "zepto": 0}
    if catalog:
        for store_name, products in (("Blinkit", b_products), ("Zepto", z_products)):
            if not products:
                continue
            store, _ = Store.objects.get_or_create(name=store_name)
            match = products[0]
            for candidate in products:
                if "amul" in candidate.name.lower() and "salted" in candidate.name.lower():
                    match = candidate
                    break
            PriceService.update_price(
                product=catalog,
                store=store,
                data={
                    "price": match.price,
                    "in_stock": match.in_stock,
                    "product_url": match.product_url,
                },
            )
            stored[store_name.lower()] = 1
            print(
                f"Stored {store_name} price Rs{match.price} "
                f"for catalog product id={catalog.id} ({catalog.name})"
            )

    report["persisted"] = stored
    report["current_prices_total"] = CurrentPrice.objects.count()
    report["history_total"] = PriceHistory.objects.count()
    report["verified"] = {
        "blinkit_live": report["providers"]["blinkit"]["count"] > 0,
        "zepto_live": report["providers"]["zepto"]["count"] > 0,
    }

    out = Path(__file__).with_name("_live_provider_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nReport:", out)
    print(json.dumps(report["verified"], indent=2))


if __name__ == "__main__":
    main()
