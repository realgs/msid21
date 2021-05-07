import requests

LIMIT = 5
URL = {'BITBAY': {'orders': 'https://api.bitbay.net/rest/trading/orderbook/',
                  'suffix': '', 'separator': '-'},
       'BITTREX': {'orders': 'https://api.bittrex.com/v3/markets/',
                   'suffix': '/orderbook', 'separator': '-'}
       }
API_RESPONSE_OPTIONS = {'BITBAY': {'code': 'status', 'info': 'errors', 'success': 'Ok'},
                        'BITTREX': {'code': 'success', 'info': 'message', 'success': True}
                        }
ORDERS_OPTION = {'BITBAY': {'buy': 'sell', 'sell': 'buy', 'price': 'ra', 'amount': 'ca'},
                 'BITTREX': {'buy': 'ask', 'sell': 'bid', 'price': 'rate', 'amount': 'quantity'}
                 }
TRANSFER_FEES = {'BITBAY': {'AAVE': 0.23, 'ALG': 258.00, 'AMLT': 965.00, 'BAT': 29.00, 'BCC': 0.001, 'BCP': 665.00,
                            'BOB': 4901.00, 'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001, 'COMP': 0.025, 'DAI': 19.00,
                            'DASH': 0.001, 'DOT': 0.10, 'EOS': 0.10, 'ETH': 0.006, 'EXY': 52.00, 'GAME': 279.00,
                            'GGC': 6.00, 'GNT': 66.00, 'GRT': 11.00, 'LINK': 1.85, 'LML': 150.00, 'LSK': 0.30,
                            'LTC': 0.001, 'LUNA': 0.02, 'MANA': 27.00, 'MKR': 0.014, 'NEU': 109.00, 'NPXS': 2240.00,
                            'OMG': 3.50, 'PAY': 278.00, 'QARK': 1133.00, 'REP': 1.55, 'SRN': 2905.00, 'SUSHI': 2.50,
                            'TRX': 1.00, 'UNI': 0.70, 'USDC': 75.50, 'USDT':	37.00, 'XBX': 3285.00, 'XIN': 5.00,
                            'XLM': 0.005, 'XRP': 0.10, 'XTZ': 0.10, 'ZEC': 0.004, 'ZRX': 16.00},
                 'BITTREX': 'https://api.bittrex.com/v3/currencies'
                 }
TRANSACTION_FEES = {'BITBAY': 0.004, 'BITTREX': 0.0025}
MARKETS = {'BITBAY': 'https://api.bitbay.net/rest/trading/ticker', 'BITTREX': 'https://api.bittrex.com/v3/markets'}


class Api:
    def __init__(self):
        self.__bitbay_transfer_fee = TRANSFER_FEES['BITBAY']
        self.__bitbay_transaction_fee = TRANSACTION_FEES['BITBAY']
        self.__bitbay_markets = self.__get_bitbay_markets()
        self.__bittrex_transfer_fee = self.__get_bittrex_transfer_fees()
        self.__bittrex_transaction_fee = TRANSACTION_FEES['BITTREX']
        self.__bittrex_markets = self.__get_bittrex_markets()

    def transfer_fee(self, api, symbol):
        if api == 'BITTREX':
            return self.__bittrex_transfer_fee[symbol]
        elif api == 'BITBAY':
            return self.__bitbay_transfer_fee[symbol]

    def transaction_fee(self, api):
        if api == 'BITTREX':
            return self.__bittrex_transaction_fee
        elif api == 'BITBAY':
            return self.__bitbay_transaction_fee

    def markets(self, api):
        if api == 'BITTREX':
            return self.__bittrex_markets
        elif api == 'BITBAY':
            return self.__bitbay_markets

    @classmethod
    def orders(cls, api, cryptocurrency, currency, orderType, depth=LIMIT):
        data = cls.__get_orders(api, cryptocurrency, currency)
        orders = []
        if data is not None:
            if 'result' in data:
                data = data['result']
            offers = data[ORDERS_OPTION[api][orderType]]
            for offer in offers[:depth]:
                order = {'price': offer[ORDERS_OPTION[api]['price']], 'amount': offer[ORDERS_OPTION[api]['amount']]}
                orders.append(order)
        return orders

    @classmethod
    def __get_bittrex_transfer_fees(cls):
        result = dict()
        respond = cls.__data_request(TRANSFER_FEES['BITTREX'])
        if not(respond is None):
            data = respond.json()
        else:
            print('get bittrex transfer fees error')
            return 1
        for currency in data:
            symbol = currency['symbol']
            result[f'{symbol}'] = currency['txFee']
        return result

    @classmethod
    def __get_bittrex_markets(cls):
        response = cls.__data_request(MARKETS['BITTREX'])
        result = []
        if not(response is None):
            for market in response.json():
                result.append(market['symbol'])
        return result

    @classmethod
    def __get_bitbay_markets(cls):
        response = cls.__data_request(MARKETS['BITBAY'])
        result = []
        data = response.json()['items'].keys()
        if not(response is None):
            for market in data:
                result.append(market)
        return result

    @classmethod
    def __get_orders(cls, api, cryptocurrency, currency):
        if not(api in URL):
            print('unknown API')
            return None
        url = URL[api]['orders'] + cryptocurrency + URL[api]['separator'] + currency + URL[api]['suffix']
        response = cls.__data_request(url)
        data = response.json()
        if API_RESPONSE_OPTIONS[api]['code'] not in data:
            return data
        elif data[API_RESPONSE_OPTIONS[api]['code']] == API_RESPONSE_OPTIONS[api]['success']:
            return data
        else:
            print(data[API_RESPONSE_OPTIONS[api]['info']])
            return None

    @staticmethod
    def __data_request(url):
        respond = requests.get(url)
        if respond.status_code != 200:
            print('HTTP response error')
            return None
        else:
            return respond
