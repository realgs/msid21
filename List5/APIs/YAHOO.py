from abc import ABC
from APIs.API import Api
from myKeys import YAHOO_KEY


class Yahoo(Api, ABC):
    def __init__(self):
        super().__init__("Yahoo", "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary")

    def orderbook(self, symbol):
        return None

    def transferFee(self, symbol):
        return None

    @property
    def takerFee(self):
        return None

    def ticker(self, symbol, base_currency=None):
        rate = 0
        stock = symbol.split('-')[0]
        currency = symbol.split('-')[1]
        querystring = {"symbol": f'{stock}', "region": "US"}
        headers = {
            'x-rapidapi-key': YAHOO_KEY,
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        try:
            data = self.data_request(f'{self.url}', headers=headers, querystring=querystring)
            rate = float(data.json()['price']['regularMarketOpen']['raw'])
        except Exception:
            pass
        return {'rate': rate, 'currency': currency}
