from API.Api import Api, request


class Bittrex(Api):
    def __init__(self):
        super().__init__('bittrex', 'https://api.bittrex.com/v3')

        fees = request(f'{self.url}/currencies')
        self.__fees = {x['symbol']: float(x['txFee']) for x in fees}

    @property
    def markets(self):
        markets = request(f'{self.url}/markets')
        return list(map(lambda x: x['symbol'], markets))

    def orderbook(self, first, second):
        orderbook = request(f'{self.url}/markets/{first}-{second}/orderbook')
        bids = list(map(lambda x: {'rate': float(x['rate']), 'quantity': float(
            x['quantity'])}, orderbook['bid']))
        asks = list(map(lambda x: {'rate': float(x['rate']), 'quantity': float(
            x['quantity'])}, orderbook['ask']))
        return asks, bids

    def transfer_fee(self, currency):
        if currency in self.__fees:
            return self.__fees[currency]
        else:
            raise ValueError(f'Unidentified currency symbol - {currency}')

    @property
    def taker_fee(self):
        return 0.0075
