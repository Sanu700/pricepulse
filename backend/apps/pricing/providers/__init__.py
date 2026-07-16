"""
Provider registry — single entry point for the rest of the app.

Usage:
    from apps.pricing.providers import get_provider, get_all_providers

    blinkit = get_provider("blinkit")
    results = blinkit.search("amul butter")
"""

from __future__ import annotations

from django.conf import settings

from .base import BaseProvider
from .bigbasket import BigBasketProvider
from .blinkit import BlinkitProvider
from .fake import FakeProvider
from .instamart import InstamartProvider
from .zepto import ZeptoProvider

# Store name in DB → provider factory
_PROVIDER_MAP: dict[str, type[BaseProvider]] = {
    "blinkit": BlinkitProvider,
    "zepto": ZeptoProvider,
    "instamart": InstamartProvider,
    "swiggy instamart": InstamartProvider,
    "bigbasket": BigBasketProvider,
}


# Per-store fake baselines so comparisons look realistic in demo mode
_FAKE_DEFAULTS = {
    "blinkit": {"base": 78.0, "spread": 22.0},
    "zepto": {"base": 82.0, "spread": 20.0},
    "instamart": {"base": 80.0, "spread": 24.0},
    "swiggy instamart": {"base": 80.0, "spread": 24.0},
    "bigbasket": {"base": 76.0, "spread": 26.0},
}


def get_provider(store_name: str) -> BaseProvider:
    """
    Return the provider for a store name.

    Respects PROVIDER_MODE:
      - fake   → always FakeProvider
      - live   → only real providers (may return empty)
      - hybrid → real provider; collector falls back to fake on empty
    """
    key = (store_name or "").strip().lower()
    try:
        mode = getattr(settings, "PROVIDER_MODE", "hybrid").lower()
    except Exception:
        mode = "hybrid"

    if mode == "fake":
        defaults = _FAKE_DEFAULTS.get(key, {"base": 80.0, "spread": 25.0})
        return FakeProvider(store_name=store_name, **defaults)

    cls = _PROVIDER_MAP.get(key)
    if cls is None:
        defaults = _FAKE_DEFAULTS.get(key, {"base": 80.0, "spread": 25.0})
        return FakeProvider(store_name=store_name, **defaults)

    return cls()


def get_fallback_provider(store_name: str) -> FakeProvider:
    key = (store_name or "").strip().lower()
    defaults = _FAKE_DEFAULTS.get(key, {"base": 80.0, "spread": 25.0})
    return FakeProvider(store_name=store_name, **defaults)


def get_all_providers() -> list[BaseProvider]:
    return [
        cls()
        for cls in (
            BlinkitProvider,
            ZeptoProvider,
            InstamartProvider,
            BigBasketProvider,
        )
    ]


__all__ = [
    "BaseProvider",
    "get_provider",
    "get_fallback_provider",
    "get_all_providers",
    "BlinkitProvider",
    "ZeptoProvider",
    "InstamartProvider",
    "BigBasketProvider",
    "FakeProvider",
]
