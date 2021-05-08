from ApiUtility import ApiUtility


class BittrexApiUtility(ApiUtility):
    def __init__(self):
        super().__init__("Bittrex", "https://api.bittrex.com/v3")
        self._fees = {}

        currencies = self.request_to_api(f"{self._api_url}/currencies")
        for currency in currencies:
            self._fees[currency['symbol']] = currency['txFee']

    def get_taker_fee(self):
        return 0.0035  # fee for: 25 000 $

    def get_transfer_fee(self, symbol):
        if symbol in self._fees:
            return float(self._fees[symbol])
        raise ValueError(f"Incorrect market symbol: {symbol}")

    def get_markets(self):
        response = self.request_to_api(f"{self._api_url}/markets")
        return list(map(lambda el: el['symbol'], response))

    def get_orderbook(self, symbol):
        response = self.request_to_api(f"{self._api_url}/markets/{symbol}/orderbook")
        bids = list(map(lambda x: [float(x['rate']), float(x['quantity'])], response['bid'][:self._offers_limit]))
        asks = list(map(lambda x: [float(x['rate']), float(x['quantity'])], response['ask'][:self._offers_limit]))
        return {'bids': bids, 'asks': asks}


if __name__ == "__main__":
    # TODO - delete - tests
    b = BittrexApiUtility()
    print(b.get_markets())
    print(b.get_orderbook('BSV-EUR'))
