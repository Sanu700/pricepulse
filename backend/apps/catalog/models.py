from django.db import models
from common.models import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    logo = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    barcode = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True
    )

    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
