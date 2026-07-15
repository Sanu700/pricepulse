"""Capture raw Blinkit/Zepto JSON for parser development."""

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


def main() -> None:
    blinkit = capture_matching_json(
        page_url="https://blinkit.com/s/?q=amul%20butter",
        url_contains="v1/layout/search",
        latitude=28.6139,
        longitude=77.2090,
        wait_ms=12000,
    )
    Path("scripts/_raw_blinkit.json").write_text(
        json.dumps(blinkit, indent=2)[:250000], encoding="utf-8"
    )
    print("blinkit", "ok" if blinkit else "FAIL", type(blinkit))

    zepto = capture_matching_json(
        page_url="https://www.zepto.com/search?query=amul%20butter",
        url_contains="user-search-service/api/v3/search",
        latitude=12.9716,
        longitude=77.5946,
        wait_ms=12000,
        method="POST",
    )
    Path("scripts/_raw_zepto.json").write_text(
        json.dumps(zepto, indent=2)[:250000], encoding="utf-8"
    )
    print("zepto", "ok" if zepto else "FAIL", type(zepto))

    # Print structure hints without rupee glyph
    if zepto:
        sample = json.dumps(zepto)[:2000]
        print("zepto sample bytes", sample.encode("ascii", "replace")[:500])


if __name__ == "__main__":
    main()
