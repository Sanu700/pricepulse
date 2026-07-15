from urllib.parse import urlparse

from django.conf import settings
from django.db import connection
from redis import Redis


class HealthService:

    @staticmethod
    def check():
        status = {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            status["status"] = "unhealthy"
            status["database"] = "disconnected"

        try:
            host = getattr(settings, "REDIS_HOST", "localhost")
            port = getattr(settings, "REDIS_PORT", 6379)

            # Prefer broker URL host when provided
            broker = getattr(settings, "CELERY_BROKER_URL", "") or ""
            if broker.startswith("redis://"):
                parsed = urlparse(broker)
                host = parsed.hostname or host
                port = parsed.port or port

            redis_client = Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            redis_client.ping()
        except Exception:
            status["status"] = "unhealthy"
            status["redis"] = "disconnected"

        return status
