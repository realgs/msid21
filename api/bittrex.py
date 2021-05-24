from api.api import Api


class Bittrex(Api):
    def __init__(self):
        super().__init__("Bittrex", "https://api.bittrex.com/v3")
        self._fees = {}

        currencies = self.request(f"{self._url}/currencies")
        for currency in currencies:
            self._fees[currency['symbol']] = currency['txFee']

    @property
    def transactionFee(self):
        return 0.0025

    def withdrawalFee(self, symbol):
        if symbol in self._fees:
            return float(self._fees[symbol])

        raise ValueError(f"Incorrect symbol: {symbol}")

    @property
    def markets(self):
        response = self.request(f"{self._url}/markets")
        return list(map(lambda el: el['symbol'], response))

    def orderbook(self, symbol):
        response = self.request(f"{self._url}/markets/{symbol}/orderbook")
        bid = list(map(lambda el: {'quantity': float(el['quantity']), 'rate': float(
            el['rate'])}, response['bid'][:self._limit]))
        ask = list(map(lambda el: {'quantity': float(el['quantity']), 'rate': float(
            el['rate'])}, response['ask'][:self._limit]))
        return {'bid': bid, 'ask': ask}

