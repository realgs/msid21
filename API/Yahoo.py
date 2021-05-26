import yfinance as yf

from API.Api import Api


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
        # TODO handle exception and check currency (info('currency'))
        ticker = yf.Ticker(stock_name)
        return (ticker.info["dayLow"] + ticker.info["dayHigh"]) / 2
