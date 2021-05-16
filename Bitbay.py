from Api import Api
from const import transfer


class Bitbay(Api):

    def __init__(self):
        super().__init__('bitbay', 'https://api.bitbay.net/rest/trading')
        self.__fees = transfer

    @property
    def markets(self):
        markets = self.request(f'{self.url}/ticker')
        return list(markets['items'].keys())

    def orderbook(self, first, second):
        orderbook = self.request(f'{self.url}/orderbook/{first}-{second}')
        asks = list(map(lambda x: {'rate': float(x['ra']), 'quantity': float(
            x['ca'])}, orderbook['sell']))
        bids = list(map(lambda x: {'rate': float(x['ra']), 'quantity': float(
            x['ca'])}, orderbook['buy']))
        return asks, bids

    def transfer_fee(self, currency):
        if currency in self.__fees:
            return self.__fees[currency]
        else:
            raise ValueError(f'Unidentified currency symbol - {currency}')

    @property
    def taker_fee(self):
        return 0.0042
