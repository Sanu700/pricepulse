# Re-export the maintained health service (avoid duplicate hardcoded host="redis").
from .health_services import HealthService

__all__ = ["HealthService"]
