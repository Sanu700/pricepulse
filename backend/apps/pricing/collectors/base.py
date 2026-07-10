from abc import ABC, abstractmethod


class BaseCollector(ABC):

    @abstractmethod
    def fetch_price(self, product):
        """
        Return:
        {
            "price": Decimal,
            "in_stock": bool
        }
        """
        pass