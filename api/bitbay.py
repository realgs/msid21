from api.api import Api


class BitBay(Api):
    def __init__(self):
        super().__init__("BitBay", "https://api.bitbay.net/rest/trading")

    @property
    def transactionFee(self):
        return 0.001

    def withdrawalFee(self, symbol):
        fees = {
            'BTC': 0.0005,
            'ETH': 0.01,
            'LTC': 0.001
        }

        if symbol in fees:
            return fees[symbol]

        raise ValueError(f"Incorrect symbol: {symbol}")

    @property
    def markets(self):
        response = self.request(f"{self._url}/stats")
        return list(response['items'].keys())

    def orderbook(self, symbol):
        raise NotImplementedError()

    @property
    def tickers(self):
        raise NotImplementedError()

    def ticker(self, symbol):
        raise NotImplementedError()
