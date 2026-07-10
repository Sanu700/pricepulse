from django.contrib import admin

from .models import Store, CurrentPrice, PriceHistory

admin.site.register(Store)
admin.site.register(CurrentPrice)
admin.site.register(PriceHistory)
