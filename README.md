# PricePulse

**Compare grocery prices across Blinkit, Zepto, Swiggy Instamart, and BigBasket — in one place.**

PricePulse is a full-stack grocery price comparison app: live (or simulated) multi-store prices, history charts, price-drop alerts, analytics, and a polished React UI. Built as a production-quality portfolio project.

---

## Overview

Shoppers waste money because the same SKU costs different amounts on Blinkit vs Zepto vs Instamart vs BigBasket. PricePulse:

1. Tracks a catalog of everyday grocery products  
2. Collects current prices per store through a provider layer  
3. Stores history for trend charts and drop detection  
4. Surfaces cheapest store, savings, and alerts in a modern web app  

Guest mode lets reviewers demo the product without registering.

---

## Features

- Multi-store price comparison (Blinkit · Zepto · Instamart · BigBasket)
- Product catalog with search, filters, and product detail pages
- Comparison table with MRP, discount %, delivery ETA, stock, and "Visit store" deep links
- Self-hosted store logos + local product placeholder (no remote CDNs, no broken images)
- Price history charts and product stats
- Dashboard analytics (drops, cheapest picks, store overview)
- Wishlist (local) + price alerts (email / console)
- JWT auth (register / login / refresh) + guest browsing
- Single normalized provider schema + hybrid FakeProvider fallback
- Playwright-backed JSON interception for all four live providers when enabled
- Concurrent multi-provider collection + 5-minute provider cache
- DB-first search with background stale refresh
- Celery beat scheduled collection
- Docker Compose one-command local stack
- OpenAPI docs via drf-spectacular

---

## Screenshots

> Placeholder slots — drop PNGs into `docs/screenshots/` when available.

| Home | Products | Product detail |
|------|----------|----------------|
| `docs/screenshots/home.png` | `docs/screenshots/products.png` | `docs/screenshots/detail.png` |

| Dashboard | Analytics | Login / Guest |
|-----------|-----------|---------------|
| `docs/screenshots/dashboard.png` | `docs/screenshots/analytics.png` | `docs/screenshots/login.png` |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6, Django REST Framework, SimpleJWT |
| Workers | Celery, django-celery-beat schedule, Redis |
| Database | PostgreSQL 17 |
| Frontend | Vite 8, React 19, React Router 7, TanStack Query 5 |
| UI | Tailwind CSS v4, Framer Motion, Recharts, Lucide |
| Providers | httpx, Playwright (optional), FakeProvider |
| Ops | Docker Compose, WhiteNoise, Gunicorn (image default) |

---

## Architecture

```
┌─────────────┐     JWT / Guest      ┌──────────────────┐
│  React SPA  │ ◄──────────────────► │  Django DRF API  │
│  :5173      │                      │  :8000           │
└─────────────┘                      └────────┬─────────┘
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     │                        │                        │
                     ▼                        ▼                        ▼
               PostgreSQL                  Redis                  Celery Worker
               (catalog,                   (broker +               + Beat
                prices,                     cache)                (collect)
                history)
                                              │
                                              ▼
                                    Provider registry
                    ┌──────────┬──────────┬───────────┬───────────┐
                    │ Blinkit  │  Zepto   │ Instamart │ BigBasket │
                    │(Playwright(Playwright(Playwright │(Playwright│
                    │  /JSON)  │  /BFF)   │  /JSON)   │/listing-  │
                    │          │          │           │  svc)     │
                    └────┬─────┴────┬─────┴─────┬─────┴─────┬─────┘
                         │          │           │           │
                         └──────────┴───────────┴───────────┘
                                 FakeProvider
                              (hybrid fallback)
```

All providers return a single normalized schema:

```
ProductResult {
  name, brand, unit, image_url, product_url,
  mrp, selling_price, in_stock, delivery_eta, source, raw
}
```

Parsing/normalization is centralized in `providers/base.py` (`build_product`,
`parse_money`, `styled_text`, `extract_unit`) so no provider duplicates logic.

---

## Folder Structure

```
pricepulse/
├── backend/
│   ├── apps/
│   │   ├── accounts/          # User + JWT register/profile
│   │   ├── catalog/           # Products, brands, categories
│   │   ├── pricing/           # Stores, prices, history, providers, Celery
│   │   └── notifications/     # Alerts + delivery
│   ├── common/                # Health, pagination
│   ├── config/                # Django settings, Celery, URLs
│   ├── scripts/               # Provider probes / verification
│   ├── entrypoint.py          # Docker boot (migrate/seed/collect)
│   └── Dockerfile
├── frontend1/frontend/        # Vite React app
├── docker-compose.yml
└── README.md
```

---

## Database Design

| Model | Purpose |
|-------|---------|
| `Product` | Catalog item (`name`, `brand`, `category`, `barcode`, `image` / `image_url`) |
| `Brand` / `Category` | Normalized taxonomy |
| `Store` | Blinkit / Zepto / Instamart / BigBasket metadata |
| `CurrentPrice` | Latest `(product, store)` price, MRP, stock, delivery ETA, product URL |
| `PriceHistory` | Append-only snapshots for charts & drops |
| `PriceAlert` | User/guest target-price subscriptions |
| `NotificationLog` | Delivery audit (staff) |
| `User` | Custom accounts model |

Unique constraint on `CurrentPrice(product, store)`. History indexed by `(product, -recorded_at)`.

---

## Provider Architecture

Each provider implements:

- `search(query)`
- `get_product(external_id)`
- `get_current_price(external_id)`
- `get_availability(external_id)`
- `get_store()`
- `fetch_price_for_catalog_product(product)` — fuzzy/barcode match into catalog

**`PROVIDER_MODE`**

| Mode | Behavior |
|------|----------|
| `fake` | Deterministic demo prices (default in Docker for clean boots) |
| `hybrid` | Try live providers → FakeProvider if empty |
| `live` | Live only (may return nothing when WAF blocks) |

Each provider follows the same flow: **optional aggregator → cold HTTP (usually
blocked) → Playwright JSON interception → DOM fallback → `[]`**. Results are
cached for 5 minutes per `(provider, query, lat/lon)`, and collection fetches
run concurrently on a thread pool (`PROVIDER_MAX_WORKERS`). Adding a new store
means dropping in `providers/new_provider.py` and registering it — no service
layer changes.

### Blinkit integration
Cold `GET https://blinkit.com/v1/layout/search` returns 403/404 outside a
browser. A Chromium session loads the same `layout/search` JSON, which we
intercept; DOM price cards are the fallback.

### Zepto integration
Public API is gone; the BFF `user-search-service/api/v3/search` returns 429 cold.
Playwright on the search page intercepts the same BFF POST (prices in paise),
with a DOM fallback.

### Swiggy Instamart integration
Instamart runs through Swiggy's authenticated APIs; anonymous `api/instamart/search`
calls are rejected. Playwright loads the Instamart search page and we intercept
the consumer JSON (product `variations`), with a DOM fallback. Falls back to
FakeProvider in hybrid mode when the session is challenged.

### BigBasket integration
`listing-svc/v2/products` is Akamai-guarded against anonymous clients. Playwright
on `bigbasket.com/ps/?q=` intercepts the `listing-svc` JSON
(`pricing.discount.prim_price.sp`, `images[].m`, `absolute_url`), with a DOM
fallback.

> **Honest note:** these platforms have no public APIs and actively block bots.
> Live capture works in a real browser session but is inherently brittle and
> region-locked. That is exactly why the hybrid `FakeProvider` fallback exists —
> demos stay populated and deterministic regardless of anti-bot state.

### Store logos & images
Store logos are **self-hosted** SVGs in `frontend/public/logos/` (no
`cdn.grofers.com` / remote logos). Product images come only from live provider
`image_url`s; when absent the UI shows a local
`public/images/product-placeholder.svg` — never random stock photography.

---

## JWT Authentication

- `POST /api/v1/accounts/register/`
- `POST /api/v1/accounts/login/` (TokenObtainPair)
- `POST /api/v1/accounts/refresh/`
- `GET /api/v1/accounts/profile/` (authenticated)

Access ≈ 30 minutes · Refresh ≈ 7 days. Frontend axios interceptor refreshes on 401 and syncs `AuthContext`.

---

## Docker Setup

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/api/docs/ |
| Health | http://localhost:8000/health/ |
| Postgres | localhost:5432 |
| Redis | localhost:6380 → container 6379 |

Compose injects env for services (no `backend/.env` required). Backend only runs migrate + seed + initial fake collect. Celery/beat skip bootstrap (`RUN_BOOTSTRAP=0`).

> Default `PROVIDER_MODE=fake` for reliable demos. For live providers: set `PROVIDER_MODE=hybrid`, `PROVIDER_USE_PLAYWRIGHT=True`, install Chromium in the image (`playwright install --with-deps chromium`), and lower `PROVIDER_MAX_WORKERS` (2–3) so concurrent browser launches stay stable.

> **Windows / OneDrive gotcha:** if `docker compose up --build` fails with
> `invalid file request Dockerfile`, the repo is inside a OneDrive folder whose
> files are cloud "reparse points" Docker can't read. Move/clone the project to a
> plain local path (e.g. `C:\dev\pricepulse`) and rebuild.

---

## Local Development

```bash
# Infra
docker compose up -d postgres redis

# Backend
cd backend
cp .env.example .env
pip install -r requirements.txt
# Optional live scrapers:
# playwright install chromium
python manage.py migrate
python manage.py seed_data
python manage.py collect_prices
python manage.py runserver

# Workers (optional)
celery -A config worker -l info
celery -A config beat -l info

# Frontend
cd frontend1/frontend
cp .env.example .env   # VITE_API_URL=http://localhost:8000/api/v1
npm install
npm run dev
```

---

## Environment Variables

See `backend/.env.example`. Highlights:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django signing key (required real value when `DEBUG=False`) |
| `PROVIDER_MODE` | `fake` \| `hybrid` \| `live` |
| `PROVIDER_USE_PLAYWRIGHT` | Enable browser JSON capture |
| `REDIS_CACHE_URL` | Shared cache for rate limits / provider responses |
| `QUICKCOMMERCE_API_KEY` | Optional paid aggregator |
| `EMAIL_*` | SMTP for real alert delivery |

Never put API keys in frontend env vars.

---

## API Documentation

Interactive OpenAPI UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

Core routes:

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/v1/products/` | Search + pagination (DB-first; `?search=` triggers async stale refresh) |
| GET | `/api/v1/products/{id}/` | Detail |
| GET | `/api/v1/prices/product/{id}/` | Current store prices (price, MRP, discount %, ETA, logo, URL) |
| GET | `/api/v1/products/{id}/history/` | History |
| GET | `/api/v1/analytics/summary/` | Dashboard aggregates |
| POST | `/api/v1/alerts/` | Create alert (guest email required) |
| GET | `/health/` | DB + Redis |

---

## Demo Instructions

1. `docker compose up --build`
2. Open http://localhost:5173/login → **Continue as guest**
3. Browse Home → Products → open **Amul Butter 500g**
4. Compare store prices, view history chart, set an alert (email required)
5. Check Dashboard / Analytics for drops and cheapest picks
6. (Optional) Register an account and use Profile

---

## Future Improvements

- Authenticated Instamart/BigBasket sessions (cookies/device tokens) for higher live hit rates
- Playwright browser pool for faster, safer concurrent hybrid collect
- Per-user cloud wishlist sync
- Production nginx multi-stage frontend image
- Stronger barcode GTINs + unit normalization
- Database-backed Celery beat admin schedules

---

## Challenges Solved

- Quick-commerce APIs are not public; reverse-engineered endpoints are WAF-guarded
- Playwright JSON interception vs brittle HTML scrape
- Catalog ↔ provider matching (name, brand, unit, barcode)
- Keeping demos stable with FakeProvider when live paths fail
- Docker boot races (migrate/seed once on backend only)
- JWT refresh queue without request hangs

---

## Why this project stands out

- End-to-end product, not a CRUD tutorial: providers → collector → history → alerts → charts
- Honest fallbacks instead of fake “integrations”
- Portfolio-ready UI (green grocery aesthetic, skeletons, empty states, guest mode)
- Ops story: Compose, Celery, Redis cache, health checks, OpenAPI

---

## Deployment

- Prefer `DEBUG=False`, strong `SECRET_KEY`, gunicorn (Dockerfile CMD), managed Postgres/Redis
- Serve frontend via static CDN/nginx (`npm run build`) with `VITE_API_URL` baked at build time
- Put docs (`/api/docs/`) behind auth or disable in production
- Do not run Playwright scrapers against production ToS without legal review — use aggregators or official APIs when available

---

## License

MIT — use freely for portfolio / learning. Grocery brand names and logos belong to their respective owners and are used for demonstration only.
