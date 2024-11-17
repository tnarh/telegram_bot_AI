from typing import Dict


class Prices:

    _PRICES = {
        'ykassa': {7: 299, 14: 600, 31: 1100},
        'stripe': {7: 3, 14: 7, 31: 12},
    }

    @classmethod
    async def get_prices_and_days(cls, payment_type: str) -> Dict:
        return cls._PRICES.get(payment_type)

