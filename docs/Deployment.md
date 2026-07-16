# Deployment

PricePulse is designed to run locally via Docker Compose and deploy as a split frontend + backend.

## Environments

### Development (recommended)
- Backend: Django dev or Gunicorn in Docker
- Frontend: Vite dev server
- Postgres + Redis: Docker

### Production
- Frontend: Vercel (static SPA)
- Backend: Render (Django + Gunicorn)
- Postgres: Neon
- Redis: Upstash

## Backend (Render)

1. Create a Render Web Service from the `backend/` directory.
2. Set runtime to Docker or use a start command:
   - `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
3. Set required env vars:
   - `DEBUG=False`
   - `SECRET_KEY=<random>`
   - `ALLOWED_HOSTS=<render-host>`
   - `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`
   - `REDIS_CACHE_URL=<upstash>` and `USE_REDIS_CACHE=True`
   - `CELERY_BROKER_URL=<upstash>` and `CELERY_RESULT_BACKEND=<upstash>`

### Migrations and seeding
Run migrations as a one-off job (Render shell or a separate job):
- `python manage.py migrate --noinput`
- `python manage.py seed_data`

Do not run `RUN_BOOTSTRAP=1` on multiple replicas.

## Workers

Create a separate Render Background Worker:
- `celery -A config worker --loglevel=info`

Optional beat:
- `celery -A config beat --loglevel=info`

## Frontend (Vercel)

1. Set project root to `frontend1/frontend`.
2. Build command: `npm run build`
3. Output: `dist`
4. Env:
   - `VITE_API_URL=<your backend>/api/v1`
   - `VITE_API_DOCS_URL=<your backend>/api/docs/` (optional)

## Provider Modes in Production

- Default to `fake` or `hybrid`.
- Live modes rely on Playwright and are subject to anti-bot restrictions and ToS.

## Scaling notes
- Cache provider searches in Redis to prevent stampedes.
- Keep history growth bounded via retention policies if traffic grows.
- Add proper observability (Sentry/log aggregation) for real deployments.