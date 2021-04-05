from stock.utils import *


class CurrencyExchanger:
    @staticmethod
    def convert(base_currency, target_currency, amount):
        if base_currency == target_currency:
            return amount

        response = connect("https://api.exchangerate.host/convert?from={0}&to={1}&amount={2}".format(base_currency, target_currency, amount))
        return response['result']
