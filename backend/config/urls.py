from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/accounts/login/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("api/v1/accounts/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.pricing.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("health/", include("common.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
