from api.api import Api
import yfinance as yf

class Yahoo(Api):
    def __init__(self):
        super().__init__("Yahoo", "http://api.nbp.pl/api/exchangerates/rates")

    def orderbook(self, symbol):
        return None

    def ticker(self, symbol):
        currency = symbol.split('-')[0]
    
        try:
            ticker = yf.Ticker(symbol)
            return {'price': (ticker['dayLow'] + ticker['dayHigh'])/2}
        except Exception:
            pass

        raise ValueError(f'Wrong symbol: {symbol}')
