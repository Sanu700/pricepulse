from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """
    Legacy collector interface.

    New price collection should use apps.pricing.providers.BaseProvider.
    Kept so existing FakeCollector imports continue to work.
    """

    @abstractmethod
    def fetch_price(self, product):
        """
        Return:
        {
            "price": Decimal,
            "in_stock": bool
        }
        """
