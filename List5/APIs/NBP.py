from abc import ABC
from APIs.API import Api


class NBP(Api, ABC):
    def __init__(self):
        super().__init__("NBP", "http://api.nbp.pl/api/exchangerates/rates/")
        self._tableSymbol = ['C']

    def orderbook(self, symbol):
        return None

    def transferFee(self, symbol):
        return None

    @property
    def takerFee(self):
        return None

    def ticker(self, currency, base_currency='PLN'):
        rate, base_rate = 0, 1
        currency = currency.split('-')[0]
        if currency == base_currency:
            print('1\n1\n')
            return 1
        if currency == 'PLN':
            for symbol in self._tableSymbol:
                try:
                    response = self.data_request(f'{self.url}/{symbol}/{currency}/')
                    rate = float(response.json()['rates'][0]['ask'])
                except Exception:
                    pass
        else:
            for symbol in self._tableSymbol:
                try:
                    response = self.data_request(f'{self.url}/{symbol}/{currency}/')
                    rate = float(response.json()['rates'][0]['ask'])
                    response = self.data_request(f'{self.url}/{symbol}/{base_currency}/')
                    base_rate = float(response.json()['rates'][0]['ask'])
                except Exception:
                    pass
        return {'rate': rate/base_rate, 'currency': currency}
