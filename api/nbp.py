from api.api import Api


class NBP(Api):
    def __init__(self):
        super().__init__("NBP", "http://api.nbp.pl/api/exchangerates/rates")
        self.__tables = ['A', 'B', 'C']

    def orderbook(self, symbol):
        return None

    def ticker(self, symbol):
        currency = symbol.split('-')[0]
        for table in self.__tables:
            url = f"{self._url}/{table}/{currency}/"
            try:
                response = self.request(url)
                return {'price': float(response['rates'][0]['mid'])}
            except ConnectionError:
                pass

        raise ValueError(f'Wrong currency: {currency}')
