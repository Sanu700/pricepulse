from django.urls import path

from .views import (
    NotificationLogListAPIView,
    NotificationStatusAPIView,
    PriceAlertListCreateAPIView,
)

urlpatterns = [
    path("alerts/", PriceAlertListCreateAPIView.as_view(), name="price-alerts"),
    path("notifications/", NotificationLogListAPIView.as_view(), name="notification-logs"),
    path(
        "notifications/status/",
        NotificationStatusAPIView.as_view(),
        name="notification-status",
    ),
]
