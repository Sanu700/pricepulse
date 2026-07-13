from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Brand, Product
from apps.pricing.models import Store


class Command(BaseCommand):
    help = "Seed sample data for PricePulse"

    def handle(self, *args, **kwargs):

        beverages, _ = Category.objects.get_or_create(name="Beverages")
        snacks, _ = Category.objects.get_or_create(name="Snacks")

        nestle, _ = Brand.objects.get_or_create(name="Nestle")
        amul, _ = Brand.objects.get_or_create(name="Amul")

        Store.objects.get_or_create(
            name="Blinkit",
            defaults={
                "logo": "https://www.blinkit.com/logo.png",
                "website": "https://www.blinkit.com",
            },
        )

        Store.objects.get_or_create(
            name="Zepto",
            defaults={
                "logo": "https://www.zepto.com/logo.png",
                "website": "https://www.zepto.com",
            },
        )

        Product.objects.get_or_create(
            barcode="8901093106545",
            defaults={
                "name": "Nestle Everyday Milk Powder",
                "brand": nestle,
                "category": beverages,
                "description": "Daily milk powder for regular use.",
            },
        )

        Product.objects.get_or_create(
            barcode="8906004922153",
            defaults={
                "name": "Amul Butter",
                "brand": amul,
                "category": beverages,
                "description": "Salted butter for everyday cooking.",
            },
        )

        Product.objects.get_or_create(
            barcode="8901164106503",
            defaults={
                "name": "Nestle KitKat Chocolate",
                "brand": nestle,
                "category": snacks,
                "description": "Classic chocolate wafer bar.",
            },
        )

        self.stdout.write(
            self.style.SUCCESS("✅ Sample data seeded successfully.")
        )
        