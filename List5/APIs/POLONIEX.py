from abc import ABC
from APIs.API import Api


class Poloniex(Api, ABC):
    def __init__(self):
        super().__init__('Poloniex', 'https://poloniex.com/public?command=', 0.00125, 0, 1)
        self._fees = {}
        currencies = self.data_request(f"{self._url}returnCurrencies")
        for currency in currencies.json():
            self._fees[currency] = currencies.json()[currency]['txFee']
        self._markets = self.markets_list

    def transferFee(self, symbol):
        if symbol in self._fees:
            return float(self._fees[symbol])
        else:
            raise ValueError(f'Incorrect symbol: {symbol}')

    @property
    def markets_list(self):
        response = self.data_request(f'{self._url}returnTicker')
        markets = []
        for pair in response.json().keys():
            pair = pair.replace('_', '-')
            markets.append(pair)
        return markets

    def orderbook(self, symbol):
        symbol = symbol.replace('-', '_')
        response = self.data_request(f'{self._url}returnOrderBook&currencyPair={symbol}')
        if symbol in self._markets:
            bids = response.json()['bids'][:self._limit]
            asks = response.json()['asks'][:self._limit]
            return {'bid': bids, 'ask': asks}
        else:
            return 0
