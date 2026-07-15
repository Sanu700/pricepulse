# PricePulse

**Compare grocery prices across Blinkit, Zepto, and Instamart — in one place.**

PricePulse is a full-stack grocery price comparison app: live (or simulated) multi-store prices, history charts, price-drop alerts, analytics, and a polished React UI. Built as a production-quality portfolio project.

---

## Overview

Shoppers waste money because the same SKU costs different amounts on Blinkit vs Zepto vs Instamart. PricePulse:

1. Tracks a catalog of everyday grocery products  
2. Collects current prices per store through a provider layer  
3. Stores history for trend charts and drop detection  
4. Surfaces cheapest store, savings, and alerts in a modern web app  

Guest mode lets reviewers demo the product without registering.

---

## Features

- Multi-store price comparison (Blinkit · Zepto · Instamart)
- Product catalog with search, filters, and product detail pages
- Price history charts and product stats
- Dashboard analytics (drops, cheapest picks, store overview)
- Wishlist (local) + price alerts (email / console)
- JWT auth (register / login / refresh) + guest browsing
- Provider architecture with hybrid FakeProvider fallback
- Playwright-backed Blinkit/Zepto capture when enabled
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
                         ┌────────────┬────────────┬────────────┐
                         │  Blinkit   │   Zepto    │ Instamart  │
                         │ (Playwright│ (Playwright│  (stub →   │
                         │  / JSON)   │  / BFF)    │   Fake)    │
                         └─────┬──────┴─────┬──────┴─────┬──────┘
                               │            │            │
                               └────────────┴────────────┘
                                      FakeProvider
                                   (hybrid fallback)
```

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
| `Store` | Blinkit / Zepto / Instamart metadata |
| `CurrentPrice` | Latest `(product, store)` price + stock + product URL |
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

**Verified live path (2026):** Blinkit/Zepto block cold HTTP (403/429). Chromium via Playwright intercepts the same consumer JSON. Optional aggregators (`QUICKCOMMERCE_API_KEY`, `PARSE_API_KEY`) are supported when keyed.

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

> Default `PROVIDER_MODE=fake` for reliable demos. For live Blinkit/Zepto: set `PROVIDER_MODE=hybrid`, `PROVIDER_USE_PLAYWRIGHT=True`, and install Chromium in the image (`playwright install --with-deps chromium`).

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
| GET | `/api/v1/products/` | Search + pagination |
| GET | `/api/v1/products/{id}/` | Detail |
| GET | `/api/v1/prices/product/{id}/` | Current store prices |
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

- Instamart live provider (auth/cookies)
- Playwright browser pool for faster hybrid collect
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
