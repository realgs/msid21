from api.api import Api


class NBP(Api):
    def __init__(self):
        super().__init__("NBP", "http://api.nbp.pl/api/exchangerates/rates")
        self.__tables = ['A', 'B', 'C']
        self.__fetched = {}

    def orderbook(self, symbol):
        return None

    def ticker(self, symbol):
        currency = symbol.split('-')[0]
        if currency in self.__fetched:
            return {'price': self.__fetched[currency]}
        else:
            for table in self.__tables:
                url = f"{self._url}/{table}/{currency}/"
                try:
                    response = self.request(url)
                    price = float(response['rates'][0]['mid'])
                    self.__fetched[currency] = price
                    return {'price': price}
                except ConnectionError:
                    pass

        raise ValueError(f'Wrong currency: {currency}')
