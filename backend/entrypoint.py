#!/usr/bin/env python
"""Container boot helper.

RUN_BOOTSTRAP=1 (backend only): wait for DB → migrate → seed → optional collect.
Celery / beat should set RUN_BOOTSTRAP=0 and just wait for DB before exec.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time


def wait_for_db(retries: int = 30) -> None:
    import psycopg

    host = os.environ.get("DB_HOST", "postgres")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    dbname = os.environ.get("DB_NAME", "pricepulse")

    for i in range(retries):
        try:
            with psycopg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname,
            ) as conn:
                conn.execute("SELECT 1")
            print("Database ready")
            return
        except Exception as exc:
            print(f"DB not ready ({i}): {exc}")
            time.sleep(2)
    raise SystemExit("Database did not become ready")


def bootstrap() -> None:
    subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])
    subprocess.check_call([sys.executable, "manage.py", "seed_data"])

    if os.environ.get("RUN_COLLECT_ON_BOOT", "0").lower() not in ("1", "true", "yes"):
        print("Skipping collect on boot (set RUN_COLLECT_ON_BOOT=1 to enable)")
        return

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from apps.pricing.models import CurrentPrice
    from apps.pricing.services.collector_services import CollectorService

    if CurrentPrice.objects.count() == 0:
        print("No prices found — collecting initial snapshot...")
        CollectorService.collect()
    else:
        print("Prices already present — skipping collect on boot")


def main() -> None:
    wait_for_db()
    if os.environ.get("RUN_BOOTSTRAP", "1").lower() in ("1", "true", "yes"):
        bootstrap()
    else:
        print("RUN_BOOTSTRAP disabled — skipping migrate/seed")

    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
    raise SystemExit("No command provided to entrypoint")


if __name__ == "__main__":
    main()
