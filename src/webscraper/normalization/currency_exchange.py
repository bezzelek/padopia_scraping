import time

from currency_converter import CurrencyConverter


class Currency:

    def __init__(self):
        self.exchange_rates = self.exchange_rates

    def collect_exchange_rate(self):
        converter = CurrencyConverter()

        currencies = ['USD', 'BGN', 'TRY']
        exchange_rates = {'EUR': 1}
        for item in currencies:
            exchange_rate = converter.convert(1, item, 'EUR')
            exchange_rates[item] = exchange_rate

            """Preventing throttling"""
            time.sleep(0.5)

        return exchange_rates

    def convert_price(self, amount, in_currency, exchange_rates):
        try:
            source_amount = int(amount)
            exchange_rate = exchange_rates[in_currency]
            price = source_amount * exchange_rate
            result = round(price)

            return result

        except:
            return None
