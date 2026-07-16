"""
Django settings for PricePulse.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-3ai!5+214r$5+wao5e&6dgo&iohqm7fg1=oi6r+^=gygzzbkmq",
)

DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,backend",
    ).split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    "apps.accounts",
    "apps.catalog",
    "apps.pricing",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.FlexiblePagination",
    "PAGE_SIZE": 48,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/min",
        "user": "300/min",
        "alert_create": "20/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "PricePulse API",
    "DESCRIPTION": "Multi-store grocery price comparison API",
    "VERSION": "1.0.0",
}

WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "accounts.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "pricepulse"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() in (
    "1",
    "true",
    "yes",
)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Asia/Kolkata")

CELERY_BEAT_SCHEDULE = {
    "collect-prices-every-30-minutes": {
        "task": "apps.pricing.tasks.collect_prices",
        "schedule": 1800.0,
    },
}

# Provider / scraping configuration
PROVIDER_MODE = os.getenv("PROVIDER_MODE", "hybrid")  # fake | hybrid | live
PROVIDER_TIMEOUT = int(os.getenv("PROVIDER_TIMEOUT", "8"))
PROVIDER_MAX_RETRIES = int(os.getenv("PROVIDER_MAX_RETRIES", "2"))
PROVIDER_RATE_LIMIT_PER_MINUTE = int(os.getenv("PROVIDER_RATE_LIMIT_PER_MINUTE", "30"))
# Provider search cache TTL (seconds). 5 minutes per the multi-provider spec.
PROVIDER_CACHE_TTL = int(os.getenv("PROVIDER_CACHE_TTL", "300"))
# Max concurrent provider fetches during collection.
PROVIDER_MAX_WORKERS = int(os.getenv("PROVIDER_MAX_WORKERS", "8"))
# How old current prices may be before a search triggers a background refresh.
PROVIDER_STALE_SECONDS = int(os.getenv("PROVIDER_STALE_SECONDS", "900"))
PROVIDER_USE_PLAYWRIGHT = os.getenv("PROVIDER_USE_PLAYWRIGHT", "True").lower() in (
    "1",
    "true",
    "yes",
)
PROVIDER_LATITUDE = float(os.getenv("PROVIDER_LATITUDE", "28.6139"))
PROVIDER_LONGITUDE = float(os.getenv("PROVIDER_LONGITUDE", "77.2090"))

# Optional paid aggregators (never expose these to the frontend)
QUICKCOMMERCE_API_KEY = os.getenv("QUICKCOMMERCE_API_KEY", "")
PARSE_API_KEY = os.getenv("PARSE_API_KEY", "")
FOODSPARK_API_KEY = os.getenv("FOODSPARK_API_KEY", "")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Prefer Redis when available so web + celery share provider cache / rate limits.
_use_redis_cache = os.getenv("USE_REDIS_CACHE", "True").lower() in ("1", "true", "yes")
if _use_redis_cache:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv(
                "REDIS_CACHE_URL",
                f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
            ),
            "KEY_PREFIX": "pricepulse",
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pricepulse-local",
            "TIMEOUT": 300,
        }
    }

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@pricepulse.local")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "apps.pricing.providers": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Production hardening (enabled when DEBUG=False)
if not DEBUG:
    if SECRET_KEY.startswith("django-insecure-") or SECRET_KEY == "dev-secret-key-change-in-production":
        raise RuntimeError("Refusing to start with an insecure SECRET_KEY when DEBUG=False")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

