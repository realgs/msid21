from api.api import Api


class BitBay(Api):
    def __init__(self):
        super().__init__("BitBay", "https://api.bitbay.net/rest/trading")

    @property
    def transactionFee(self):
        return 0.001

    def withdrawalFee(self, symbol):
        fees = {
            'AAVE':	0.23,
            'ALG':	258.00,
            'AMLT':	965.00,
            'BAT':	29.00,
            'BCC':	0.001,
            'BCP':	665.00,
            'BOB':	4901.00,
            'BSV':	0.003,
            'BTC':	0.0005,
            'BTG':	0.001,
            'COMP':	0.025,
            'DAI':	19.00,
            'DASH':	0.001,
            'DOT':	0.10,
            'EOS':	0.10,
            'ETH':	0.006,
            'EXY':	52.00,
            'GAME':	279.00,
            'GGC':	6.00,
            'GNT':	66.00,
            'GRT':	11.00,
            'LINK':	1.85,
            'LML':	150.00,
            'LSK':	0.30,
            'LTC':	0.001,
            'LUNA':	0.02,
            'MANA':	27.00,
            'MKR':	0.014,
            'NEU':	109.00,
            'NPXS':	2240.00,
            'OMG':	3.50,
            'PAY':	278.00,
            'QARK':	1133.00,
            'REP':	1.55,
            'SRN':	2905.00,
            'SUSHI':2.50,
            'TRX':	1.00,
            'UNI':	0.70,
            'USDC':	75.50,
            'USDT':	37.00,
            'XBX':	3285.00,
            'XIN':	5.00,
            'XLM':	0.005,
            'XRP':	0.10,
            'XTZ':	0.10,
            'ZEC':	0.004,
            'ZRX':	16.00
        }

        if symbol in fees:
            return fees[symbol]

        raise ValueError(f"Incorrect symbol: {symbol}")

    @property
    def markets(self):
        response = self.request(f"{self._url}/stats")
        return list(response['items'].keys())

    def orderbook(self, symbol):
        response = self.request(f"{self._url}/orderbook/{symbol}")
        bid = list(map(lambda el: {'quantity': float(el['ca']), 'rate': float(
            el['ra'])}, response['buy'][:self._limit]))
        ask = list(map(lambda el: {'quantity': float(el['ca']), 'rate': float(
            el['ra'])}, response['sell'][:self._limit]))
        return {'bid': bid, 'ask': ask}
