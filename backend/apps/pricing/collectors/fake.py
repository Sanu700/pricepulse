import random
from decimal import Decimal

from .base import BaseCollector


class FakeCollector(BaseCollector):

    def fetch_price(self, product):

        return {
            "price": Decimal(
                str(round(random.uniform(40, 120), 2))
            ),
            "in_stock": random.choice(
                [True, True, True, False]
            ),
        }