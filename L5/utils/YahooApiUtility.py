import yfinance as yf


import utils.ApiUtility as ApiUtility
import utils.NBPApiUtility as NBPUtility


class YahooApiUtility(ApiUtility.ApiUtility):

    def __init__(self):
        super().__init__("Yahoo", "")

    def get_taker_fee(self):
        raise NotImplementedError()

    def get_transfer_fee(self, symbol):
        raise NotImplementedError()

    def get_markets(self):
        raise NotImplementedError()

    def if_orderbook_supported(self):
        return False

    def get_orderbook(self, symbol):
        raise NotImplementedError()

    def get_ticker(self, symbol, base_currency):
        try:
            ticker = yf.Ticker(symbol)
            return NBPUtility.NBPApiUtility().get_ticker('USD', base_currency, (float(ticker.info['dayLow']) +
                                                                                float(ticker.info['dayHigh'])) / 2)
        except Exception:
            raise ValueError(f'Wrong symbol: {symbol}')
