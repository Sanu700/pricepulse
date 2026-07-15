"""Capture raw JSON and print product field paths (ASCII only)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from apps.pricing.providers.browser import capture_matching_json  # noqa: E402


def find_keys(obj, want, path="", hits=None, limit=20):
    hits = [] if hits is None else hits
    if len(hits) >= limit:
        return hits
    if isinstance(obj, dict):
        keys = set(obj)
        if len(want & keys) >= 2:
            slim = {}
            for k in want:
                if k not in obj:
                    continue
                v = obj[k]
                if isinstance(v, dict):
                    slim[k] = sorted(v.keys())[:12]
                elif isinstance(v, list):
                    slim[k] = f"list[{len(v)}]"
                else:
                    slim[k] = repr(v)[:80]
            hits.append((path, slim))
        for k, v in obj.items():
            find_keys(v, want, f"{path}.{k}", hits, limit)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            find_keys(v, want, f"{path}[{i}]", hits, limit)
    return hits


def main() -> None:
    blinkit = capture_matching_json(
        page_url="https://blinkit.com/s/?q=amul%20butter",
        url_contains="v1/layout/search",
        latitude=28.6139,
        longitude=77.2090,
        wait_ms=12000,
    )
    zepto = capture_matching_json(
        page_url="https://www.zepto.com/search?query=amul%20butter",
        url_contains="user-search-service/api/v3/search",
        latitude=12.9716,
        longitude=77.5946,
        wait_ms=12000,
        method="POST",
    )

    Path("scripts/_raw_blinkit.json").write_text(
        json.dumps(blinkit, ensure_ascii=True), encoding="utf-8"
    )
    Path("scripts/_raw_zepto.json").write_text(
        json.dumps(zepto, ensure_ascii=True), encoding="utf-8"
    )

    print("BLINKIT")
    for path, slim in find_keys(
        blinkit,
        {"name", "mrp", "selling_price", "normal_price", "product_id", "inventory", "unit", "brand", "image_url"},
    ):
        print(path[:100], slim)

    print("ZEPTO")
    for path, slim in find_keys(
        zepto,
        {
            "name",
            "discountedSellingPrice",
            "sellingPrice",
            "mrp",
            "productVariant",
            "brand",
            "outOfStock",
            "productResponse",
            "formattedPacksize",
        },
    ):
        print(path[:110], slim)


if __name__ == "__main__":
    main()
