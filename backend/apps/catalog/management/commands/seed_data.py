from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Product
from apps.pricing.models import Store


# Stable Unsplash grocery imagery for demos (provider URLs overwrite when live collect runs).
SAMPLE_PRODUCTS = [
    {
        "barcode": "8901093106545",
        "name": "Nestle Everyday Dairy Whitener 400g",
        "brand": "Nestle",
        "category": "Dairy",
        "description": "Dairy whitener for tea and coffee.",
        "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8906004922153",
        "name": "Amul Butter 500g",
        "brand": "Amul",
        "category": "Dairy",
        "description": "Salted butter for everyday cooking.",
        "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901164106503",
        "name": "Nestle KitKat 4 Finger",
        "brand": "Nestle",
        "category": "Snacks",
        "description": "Classic chocolate wafer bar.",
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901262010016",
        "name": "Tata Salt 1kg",
        "brand": "Tata",
        "category": "Staples",
        "description": "Iodized salt for daily cooking.",
        "image_url": "https://images.unsplash.com/photo-1606914501449-5a96b6afe27a?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901030865521",
        "name": "Aashirvaad Atta 5kg",
        "brand": "Aashirvaad",
        "category": "Staples",
        "description": "Whole wheat flour for soft rotis.",
        "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901030869122",
        "name": "Fortune Sunflower Oil 1L",
        "brand": "Fortune",
        "category": "Staples",
        "description": "Refined sunflower oil.",
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901058000158",
        "name": "Amul Gold Milk 1L",
        "brand": "Amul",
        "category": "Dairy",
        "description": "Full cream toned milk.",
        "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901030694252",
        "name": "Maggi 2-Minute Noodles 560g",
        "brand": "Nestle",
        "category": "Snacks",
        "description": "Family pack instant noodles.",
        "image_url": "https://images.unsplash.com/photo-1612929632979-711df840bfd2?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901491101837",
        "name": "Lay's Classic Salted 52g",
        "brand": "Lay's",
        "category": "Snacks",
        "description": "Crispy salted potato chips.",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901030860014",
        "name": "Surf Excel Matic 2kg",
        "brand": "Surf Excel",
        "category": "Household",
        "description": "Front-load detergent powder.",
        "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901030654792",
        "name": "Red Label Tea 500g",
        "brand": "Brooke Bond",
        "category": "Beverages",
        "description": "Strong leaf tea for everyday chai.",
        "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?auto=format&fit=crop&w=400&q=80",
    },
    {
        "barcode": "8901262020077",
        "name": "Tata Sampann Toor Dal 1kg",
        "brand": "Tata",
        "category": "Staples",
        "description": "Unpolished toor dal.",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80",
    },
]


STORES = [
    {
        "name": "Blinkit",
        "logo": "https://cdn.grofers.com/assets/icon/blinkit.png",
        "website": "https://blinkit.com",
    },
    {
        "name": "Zepto",
        "logo": "https://www.zeptonow.com/favicon.ico",
        "website": "https://www.zeptonow.com",
    },
    {
        "name": "Instamart",
        "logo": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/InstamartAssets/Instamart_logo.png",
        "website": "https://www.swiggy.com/instamart",
    },
]


class Command(BaseCommand):
    help = "Seed sample catalog, brands, and grocery stores for PricePulse"

    def handle(self, *args, **kwargs):
        for store in STORES:
            Store.objects.get_or_create(
                name=store["name"],
                defaults={"logo": store["logo"], "website": store["website"]},
            )

        for item in SAMPLE_PRODUCTS:
            category, _ = Category.objects.get_or_create(name=item["category"])
            brand, _ = Brand.objects.get_or_create(name=item["brand"])
            product, created = Product.objects.get_or_create(
                barcode=item["barcode"],
                defaults={
                    "name": item["name"],
                    "brand": brand,
                    "category": category,
                    "description": item["description"],
                    "image_url": item.get("image_url"),
                },
            )
            if not created and not product.image_url and item.get("image_url"):
                product.image_url = item["image_url"]
                product.save(update_fields=["image_url", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(SAMPLE_PRODUCTS)} products across {len(STORES)} stores."
            )
        )
