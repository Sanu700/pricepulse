# Architecture

This document explains PricePulse request flow, collection flow, and key design decisions.

## High-Level Diagram

```mermaid
flowchart LR
  FE[React SPA] -->|HTTP| API[Django DRF]
  API --> PG[(PostgreSQL)]
  API --> R[(Redis cache)]
  API --> CEL[Celery worker]
  CEL --> PG
  CEL --> R

  subgraph Providers
    BL[Blinkit]
    ZP[Zepto]
    IM[Instamart]
    BB[BigBasket]
    FK[FakeProvider]
  end

  CEL -->|fetch + normalize| BL
  CEL -->|fetch + normalize| ZP
  CEL -->|fetch + normalize| IM
  CEL -->|fetch + normalize| BB
  CEL -->|fallback| FK
```

## Request Flow

### Product list / search
1. Client calls `GET /api/v1/products/?search=...`
2. Backend returns catalog products + aggregated cheapest/highest via `CurrentPrice`.
3. If results are stale, backend triggers a background refresh task (deduped by cache lock).

### Product details
1. Client calls `GET /api/v1/products/<id>/`
2. Client calls `GET /api/v1/products/<id>/prices/` (preferred) with nested store rows.
3. Client calls `GET /api/v1/products/<id>/history/` and `/stats/` for charts and stats.

## Collection Flow

```mermaid
sequenceDiagram
  participant Beat as Celery Beat
  participant Worker as Celery Worker
  participant Provider as Provider Registry
  participant DB as Postgres

  Beat->>Worker: collect_prices
  loop product × store
    Worker->>Provider: fetch_price_for_catalog_product
    Provider-->>Worker: normalized data | None
    Worker->>DB: upsert CurrentPrice + append PriceHistory
  end
```

## Provider Normalization
- All providers emit the same normalized fields via `providers/base.py` (`build_product`).
- Live providers are best-effort; hybrid mode keeps the product experience stable.

## Caching
- Provider search responses are cached per `(provider, query, lat, lon)` for 5 minutes.
- Search freshness uses a short-lived cache lock to prevent stampedes.

## Trade-offs
- Live scraping is inherently brittle (anti-bot + region + session). The project chooses a hybrid fallback so the product remains usable and demoable.