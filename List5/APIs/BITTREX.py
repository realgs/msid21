from abc import ABC
from APIs.API import Api


class Bittrex(Api, ABC):
    def __init__(self):
        super().__init__('Bittrex', 'https://api.bittrex.com/v3', 0.0025, 'rate', 'quantity')
        self._fees = {}
        currencies = self.data_request(f"{self._url}/currencies")
        for currency in currencies.json():
            self._fees[currency['symbol']] = currency['txFee']
        self._markets = self.markets_list

    def transferFee(self, symbol):
        if symbol in self._fees:
            return float(self._fees[symbol])
        else:
            raise ValueError(f'Incorrect symbol: {symbol}')

    @property
    def markets_list(self):
        response = self.data_request(f'{self._url}/markets')
        markets = []
        for market in response.json():
            markets.append(market['symbol'])
        return markets

    def orderbook(self, symbol):
        response = self.data_request(f'{self._url}/markets/{symbol}/orderbook')
        if symbol in self._markets:
            bids = response.json()['bid'][:self._limit]
            asks = response.json()['ask'][:self._limit]
            return {'bid': bids, 'ask': asks}
        else:
            return 0
