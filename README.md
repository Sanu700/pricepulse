# PricePulse

Compare grocery prices across **Blinkit**, **Zepto**, and **Instamart**.

## Stack

- **Backend:** Django 6 + DRF + SimpleJWT + Celery + Redis + PostgreSQL
- **Frontend:** Vite + React 19 + TanStack Query + Tailwind CSS v4 + Recharts
- **Orchestration:** Docker Compose

## Quick start (Docker)

```bash
docker compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:5173        |
| Backend   | http://localhost:8000        |
| API docs  | http://localhost:8000/api/docs/ |
| Health    | http://localhost:8000/health/ |

On startup the backend runs migrations, seeds sample products/stores, and collects an initial price snapshot.

### Guest Mode

Open http://localhost:5173/login and click **Continue as guest**. No account required for browsing and comparing.

### Auth

Register or sign in from the login page. JWT access tokens last 30 minutes; refresh tokens last 7 days.

## Local development (without Docker frontend)

```bash
# Terminal 1 — infra
docker compose up postgres redis -d

# Terminal 2 — backend
cd backend
cp .env.example .env   # set DB_HOST=localhost, REDIS / Celery to localhost:6380
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py collect_prices
python manage.py runserver

# Terminal 3 — frontend
cd frontend1/frontend
cp .env.example .env
npm install
npm run dev
```

## Provider architecture

Providers live under `backend/apps/pricing/providers/`:

- `blinkit.py` / `zepto.py` / `instamart.py` — real HTTP integrations (best-effort)
- `fake.py` — deterministic demo prices
- Common interface: `search()`, `get_product()`, `get_price()`, `fetch_price_for_catalog_product()`

`PROVIDER_MODE` in `.env`:

| Value    | Behaviour |
|----------|-----------|
| `fake`   | Always simulated prices |
| `hybrid` | Try live APIs, fall back to fake (default) |
| `live`   | Live only (may return empty when APIs block) |

Blinkit / Zepto / Instamart block anonymous scrapers (geo/auth/anti-bot). Hybrid mode keeps the portfolio app usable while keeping provider modules ready for real credentials later.

## Useful commands

```bash
python manage.py seed_data
python manage.py collect_prices
celery -A config worker -l info
celery -A config beat -l info
```

## Environment

See `backend/.env.example` and `frontend1/frontend/.env.example`.
