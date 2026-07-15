# Generated manually for PricePulse v1.0 image URL support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_remove_product_image_url_category_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["name"], name="catalog_pro_name_f8bd91_idx"),
        ),
    ]
