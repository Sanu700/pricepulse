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

        # -----------------------------
        # Database Health Check
        # -----------------------------
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            status["status"] = "unhealthy"
            status["database"] = "disconnected"

        # -----------------------------
        # Redis Health Check
        # -----------------------------
        try:
            redis_url = getattr(settings, "REDIS_URL", "")

            if redis_url:
                redis_client = Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                redis_client.ping()
            else:
                status["redis"] = "not configured"

        except Exception:
            # Redis is optional for app availability
            status["redis"] = "disconnected"

        return status