from currency_converter import CurrencyConverter
import marketApi
import consts
import main

class CurrencyMarket(marketApi.Market):
    def __init__(self, name):
        super().__init__(name, consts.CURRENCY["type"])
        self.__converter = CurrencyConverter()

    def getSellPrice(self, symbol, volume, percentage):
        try:
            return round(self.__converter.convert(volume, symbol, main.WALLET["base currency"]) * percentage / 100, 2)
        except ValueError:
            return -1
            