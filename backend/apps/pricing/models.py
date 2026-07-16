from django.db import models


class Store(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    logo = models.URLField(
        blank=True,
        null=True,
    )

    website = models.URLField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CurrentPrice(models.Model):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="current_prices",
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="current_prices",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    in_stock = models.BooleanField(
        default=True,
    )

    product_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    delivery_eta = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    last_updated = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["product__name", "store__name"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "store"],
                name="unique_product_store",
            )
        ]

        indexes = [
            models.Index(
                fields=["product"],
            ),
            models.Index(
                fields=["store"],
            ),
        ]

    def __str__(self):
        return f"{self.product} | {self.store} | ₹{self.price}"


class PriceHistory(models.Model):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="price_history",
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="price_history",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    in_stock = models.BooleanField(
        default=True,
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-recorded_at"]

        indexes = [
            models.Index(
                fields=["product", "-recorded_at"],
            ),
            models.Index(
                fields=["store", "-recorded_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.product} | "
            f"{self.store} | "
            f"₹{self.price} | "
            f"{self.recorded_at:%d-%m-%Y %H:%M}"
        )