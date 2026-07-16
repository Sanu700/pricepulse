# Provider Architecture

PricePulse integrates multiple grocery platforms behind a single provider abstraction.

## Normalized Schema

All providers must produce:

```text
ProductResult {
  name, brand, unit,
  image_url, product_url,
  mrp, selling_price,
  in_stock, delivery_eta,
  source, raw
}
```

Normalization lives in `backend/apps/pricing/providers/base.py`:
- `styled_text()` for provider-specific "text wrapper" objects
- `parse_money()` for INR / paise parsing
- `extract_unit()` and matching helpers
- `build_product()` as the single normalization entry point

## Provider Flow

Each provider follows:
1. Optional aggregator (if API keys exist)
2. Cold HTTP (often blocked)
3. Playwright JSON interception (best-effort)
4. DOM fallback (heuristic)
5. Return `[]` to allow hybrid fallback

## Hybrid Mode

`PROVIDER_MODE`:
- `fake`: deterministic demo prices only
- `hybrid`: live providers then `FakeProvider` if empty
- `live`: live only

Hybrid mode exists to keep the product stable when providers block automated access.

## Caching

- Provider search calls are cached for 5 minutes with a key including provider + query + lat/lon.
- Collection uses concurrency controls (`PROVIDER_MAX_WORKERS`).

## Adding a New Provider

1. Create `backend/apps/pricing/providers/<new>.py` implementing `BaseProvider`.
2. Use `build_product()` to normalize.
3. Register in `backend/apps/pricing/providers/__init__.py`.
4. Add a local logo under `frontend1/frontend/public/logos/<new>.svg`.