# Adds MRP, delivery ETA, and widens product_url for multi-provider support.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="currentprice",
            name="mrp",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="currentprice",
            name="delivery_eta",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="currentprice",
            name="product_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
