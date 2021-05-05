from api.api import Api


class Bittrex(Api):
    def __init__(self):
        super().__init__("Bittrex", "https://api.bittrex.com/v3")

    @property
    def transactionFee(self):
        return 0.0025

    def withdrawalFee(self, symbol):
        raise NotImplementedError()

    @property
    def markets(self):
        response = self.request(f"{self._url}/markets")
        return list(map(lambda el: el['symbol'], response))

    def orderbook(self, symbol):
        raise NotImplementedError()

    @property
    def tickers(self):
        raise NotImplementedError()

    def ticker(self, symbol):
        raise NotImplementedError()

