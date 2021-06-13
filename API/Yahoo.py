import yfinance as yf

from API.Api import Api
from API.NBP import NBP


class Yahoo(Api):
    def markets(self):
        pass

    def orderbook(self, first, second):
        pass

    def transfer_fee(self, currency):
        pass

    def taker_fee(self):
        pass

    def __init__(self):
        super().__init__('Yahoo', "")

    @classmethod
    def get_price(cls, stock_name, base_currency):
        ticker = yf.Ticker(stock_name)
        price = (ticker.info["dayLow"] + ticker.info["dayHigh"]) / 2
        if ticker.info['currency'] == base_currency:
            return price
        else:
            return NBP().convert(ticker.info['currency'], price, base_currency)
