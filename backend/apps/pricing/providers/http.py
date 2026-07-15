"""
Shared HTTP helpers for grocery providers.

Includes timeouts, retries, and a simple per-provider rate limiter
backed by Django's cache.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import httpx
from django.conf import settings
from django.core.cache import cache
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
}


class ProviderError(Exception):
    """Raised when a provider request fails permanently."""


class RateLimitExceeded(ProviderError):
    """Raised when the local rate limiter rejects a request."""


def _rate_limit_key(provider: str) -> str:
    return f"provider:ratelimit:{provider}:{int(time.time() // 60)}"


def enforce_rate_limit(provider: str) -> None:
    limit = getattr(settings, "PROVIDER_RATE_LIMIT_PER_MINUTE", 30)
    key = _rate_limit_key(provider)
    try:
        count = cache.get(key, 0)
        if count >= limit:
            raise RateLimitExceeded(f"{provider} rate limit ({limit}/min) exceeded")
        cache.set(key, count + 1, timeout=70)
    except RateLimitExceeded:
        raise
    except Exception:
        # Cache failures should not block collection
        logger.debug("Rate-limit cache unavailable; continuing")


def http_get(
    url: str,
    *,
    provider: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: Optional[float] = None,
) -> httpx.Response:
    retries = max(1, int(getattr(settings, "PROVIDER_MAX_RETRIES", 2)) + 1)

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        stop=stop_after_attempt(retries),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    def _do_get() -> httpx.Response:
        enforce_rate_limit(provider)
        req_timeout = timeout or getattr(settings, "PROVIDER_TIMEOUT", 8)
        merged = {**DEFAULT_HEADERS, **(headers or {})}
        with httpx.Client(timeout=req_timeout, follow_redirects=True) as client:
            response = client.get(url, params=params, headers=merged)
            response.raise_for_status()
            return response

    return _do_get()


def http_get_json(
    url: str,
    *,
    provider: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Any:
    response = http_get(url, provider=provider, params=params, headers=headers)
    return response.json()


def cached_json(cache_key: str, ttl: int, loader):
    """Return cached JSON or call loader() and store the result."""
    # Sanitize keys for cache backends that reject spaces/special chars
    safe_key = "".join(ch if ch.isalnum() or ch in "._-:" else "_" for ch in cache_key)[:200]
    try:
        cached = cache.get(safe_key)
        if cached is not None:
            return cached
    except Exception:
        cached = None

    data = loader()
    try:
        cache.set(safe_key, data, timeout=ttl)
    except Exception:
        pass
    return data
