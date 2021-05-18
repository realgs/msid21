import Endpoint as ep


class Apis:

    def __init__(self):
        self.__bitbay = ep.Endpoint("BITBAY", "https://bitbay.net/API/Public/{}{}/orderbook.json",
                                    "https://api.bitbay.net/rest/trading/ticker", 0.043,
                                    {'AAVE': 0.54, 'ALG': 426.0, 'AMLT': 1743.0, 'BAT': 156.0, 'BCC': 0.001,
                                     'BCP': 1237.0, 'BOB': 11645.0, 'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001,
                                     'COMP': 0.1, 'DAI': 81.0, 'DASH': 0.001, 'DOT': 0.1, 'EOS': 0.1, 'ETH': 0.006,
                                     'EXY': 520.0, 'GAME': 479.0, 'GGC': 112.0, 'GNT': 403.0, 'GRT': 84.0, 'LINK': 2.7,
                                     'LML': 1500.0, 'LSK': 0.3, 'LTC': 0.001, 'LUNA': 0.02, 'MANA': 100.0, 'MKR': 0.025,
                                     'NEU': 572.0, 'NPXS': 46451.0, 'OMG': 14.0, 'PAY': 1523.0, 'QARK': 1019.0,
                                     'REP': 3.2, 'SRN': 5717.0, 'SUSHI': 8.8, 'TRX': 1.0, 'UNI': 2.5, 'USDC': 125.0,
                                     'USDT': 190.0, 'XBX': 6608.0, 'XIN': 5.0, 'XLM': 0.005, 'XRP': 0.1, 'XTZ': 0.1,
                                     'ZEC': 0.004, 'ZRX': 56.0})
        self.__bittrex = ep.Endpoint("BITTREX",
                                     "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both",
                                     "https://api.bittrex.com/v3/markets", 0.025,
                                     {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42,
                                      'DOT': 0.5, 'EOS': 0.1, 'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0,
                                      'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095,
                                      'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1,
                                      'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25})

    @property
    def bitbay(self):
        return self.__bitbay

    @property
    def bittrex(self):
        return self.__bittrex
