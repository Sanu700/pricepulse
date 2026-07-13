from django.db import connection
from redis import Redis
from django.conf import settings


class HealthService:

    @staticmethod
    def check():
        status = {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
        }

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            status["status"] = "unhealthy"
            status["database"] = "disconnected"

        # Redis check
        try:
            redis_client = Redis(
                host="redis",
                port=6379,
                decode_responses=True,
            )
            redis_client.ping()
        except Exception:
            status["status"] = "unhealthy"
            status["redis"] = "disconnected"

        return status