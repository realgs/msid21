from api.api import Api
import yfinance as yf


class Yahoo(Api):
    def __init__(self):
        super().__init__("Nasdaq", "http://api.nbp.pl/api/exchangerates/rates")

    def orderbook(self, symbol):
        return None

    def ticker(self, symbol):
        currency = symbol.split('-')[0]
        try:
            ticker = yf.Ticker(currency)
            return {'price': (float(ticker.info['dayLow']) + float(ticker.info['dayHigh']))/2}
        except Exception:
            pass

        raise ValueError(f'Wrong symbol: {symbol}')
