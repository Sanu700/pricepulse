from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Brand, Category, Product


class NotificationPermissionsTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name="Dairy")
        brand = Brand.objects.create(name="Amul")
        self.product = Product.objects.create(
            name="Amul Butter 500g",
            barcode="1234567890123",
            brand=brand,
            category=category,
        )
        self.user_model = get_user_model()

    def test_notification_status_requires_admin(self):
        response = self.client.get("/api/v1/notifications/status/")
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_authenticated_user_cannot_set_third_party_alert_email(self):
        user = self.user_model.objects.create_user(
            username="alice",
            password="Secret123!",
            email="alice@example.com",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/v1/alerts/",
            {
                "product": self.product.id,
                "target_price": str(Decimal("199.00")),
                "email": "other@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_authenticated_user_defaults_to_account_email(self):
        user = self.user_model.objects.create_user(
            username="bob",
            password="Secret123!",
            email="bob@example.com",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/v1/alerts/",
            {
                "product": self.product.id,
                "target_price": str(Decimal("149.00")),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["product"], self.product.id)
