from abc import ABC
from APIs.API import Api


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
            'x-rapidapi-key': "d8ca471437mshf1f4c0a33939a4ap1aef02jsnd0656acd8f28",
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        try:
            data = self.data_request(f'{self.url}', headers=headers, querystring=querystring)
            rate = float(data.json()['price']['regularMarketOpen']['raw'])
        except Exception:
            pass
        return {'rate': rate, 'currency': currency}
