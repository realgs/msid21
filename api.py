import requests
from bs4 import BeautifulSoup
import yahoo_code

LIMIT = 5
BITBAY = 'BITBAY'
BITTREX = 'BITTREX'
NBP = 'NBP'
YAHOO = 'YAHOO'
STOOQ = 'STOOQ'
URL = {BITBAY: {'orders': 'https://api.bitbay.net/rest/trading/orderbook/',
                'suffix': '', 'separator': '-', 'markets': 'https://api.bitbay.net/rest/trading/ticker'},
       BITTREX: {'orders': 'https://api.bittrex.com/v3/markets/',
                 'suffix': '/orderbook', 'separator': '-', 'markets': 'https://api.bittrex.com/v3/markets'},
       NBP: {'orders': None, 'markets': 'http://api.nbp.pl/api/exchangerates/rates/c/', 'suffix': '/?format=json'},
       YAHOO: {'orders': None, 'markets':  'https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary'},
       STOOQ: {'orders': None, 'markets': 'https://stooq.pl'}
       }
API_RESPONSE_OPTIONS = {BITBAY: {'code': 'status', 'info': 'errors', 'success': 'Ok'},
                        BITTREX: {'code': 'success', 'info': 'message', 'success': True}
                        }
ORDERS_OPTION = {BITBAY: {'buy': 'sell', 'sell': 'buy', 'rate': 'ra', 'amount': 'ca'},
                 BITTREX: {'buy': 'ask', 'sell': 'bid', 'rate': 'rate', 'amount': 'quantity'}
                 }
TRANSFER_FEES = {BITBAY: {'AAVE': 0.23, 'ALG': 258.00, 'AMLT': 965.00, 'BAT': 29.00, 'BCC': 0.001, 'BCP': 665.00,
                          'BOB': 4901.00, 'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001, 'COMP': 0.025, 'DAI': 19.00,
                          'DASH': 0.001, 'DOT': 0.10, 'EOS': 0.10, 'ETH': 0.006, 'EXY': 52.00, 'GAME': 279.00,
                          'GGC': 6.00, 'GNT': 66.00, 'GRT': 11.00, 'LINK': 1.85, 'LML': 150.00, 'LSK': 0.30,
                          'LTC': 0.001, 'LUNA': 0.02, 'MANA': 27.00, 'MKR': 0.014, 'NEU': 109.00, 'NPXS': 2240.00,
                          'OMG': 3.50, 'PAY': 278.00, 'QARK': 1133.00, 'REP': 1.55, 'SRN': 2905.00, 'SUSHI': 2.50,
                          'TRX': 1.00, 'UNI': 0.70, 'USDC': 75.50, 'USDT':	37.00, 'XBX': 3285.00, 'XIN': 5.00,
                          'XLM': 0.005, 'XRP': 0.10, 'XTZ': 0.10, 'ZEC': 0.004, 'ZRX': 16.00},
                 BITTREX: 'https://api.bittrex.com/v3/currencies'
                 }
TRANSACTION_FEES = {BITBAY: 0.004, BITTREX: 0.0025}


class Api:
    def __init__(self):
        self.__bitbay_transfer_fee = TRANSFER_FEES[BITBAY]
        self.__bitbay_transaction_fee = TRANSACTION_FEES[BITBAY]
        self.__bitbay_markets = self.__get_bitbay_markets()
        self.__bittrex_transfer_fee = self.__get_bittrex_transfer_fees()
        self.__bittrex_transaction_fee = TRANSACTION_FEES[BITTREX]
        self.__bittrex_markets = self.__get_bittrex_markets()
        self.__nbp_rate = {}

    def transfer_fee(self, api, symbol):
        if api == BITTREX:
            return self.__bittrex_transfer_fee[symbol]
        elif api == BITBAY:
            return self.__bitbay_transfer_fee[symbol]
        else:
            return None

    def transaction_fee(self, api):
        if api == BITTREX:
            return self.__bittrex_transaction_fee
        elif api == BITBAY:
            return self.__bitbay_transaction_fee
        else:
            return None

    def markets(self, api):
        if api == BITTREX:
            return self.__bittrex_markets
        elif api == BITBAY:
            return self.__bitbay_markets
        else:
            return None

    def last_rate(self, api, market):
        if api == NBP:
            return self.__get_nbp_rate(market)
        elif api == YAHOO:
            return self.__get_yahoo_rate(market)
        elif api == STOOQ:
            return self.__get_stooq_rate(market)

    def __get_nbp_rate(self, market):
        if market in self.__nbp_rate.keys():
            return {'rate': self.__nbp_rate[market], 'amount': None}
        base = market.split('-')[0]
        target = market.split('-')[1]
        data = self.__data_request(URL[NBP]['markets'] + f'{base}' + URL[NBP]['suffix']).json()
        rate = float(data['rates'][0]['bid'])
        if target != 'PLN':
            rate2 = 1 / self.__get_nbp_rate(f'{target}-PLN')['rate']
            rate *= rate2
        self.__nbp_rate[market] = rate
        return {'rate': rate, 'amount': None}

    def __get_yahoo_rate(self, market):
        stock = market.split('-')[0]
        currency = market.split('-')[1]
        querystring = {"symbol": f'{stock}', "region": "US"}
        headers = {
            'x-rapidapi-key': f'{yahoo_code.CODE}',
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        data = self.__data_request(URL[YAHOO]['markets'], headers=headers, querystring=querystring)
        rate = float(data.json()['price']['regularMarketOpen']['raw'])
        if currency != 'USD':
            rate2 = self.__get_nbp_rate(f'USD-{currency}')
            rate *= rate2['rate']
        return {'rate': rate, 'amount': None}

    def __get_stooq_rate(self, market):
        stock = market.split('-')[0]
        currency = market.split('-')[1]
        url = URL[STOOQ]['markets'] + f'/q/?s={stock.lower()}'
        data = self.__data_request(url).text
        parser = BeautifulSoup(data, 'html.parser')
        rate = float(parser.find(id="t1").find('td').find('span').text)
        if currency != 'PLN':
            rate2 = 1 / self.__get_nbp_rate(f'{currency}-PLN')['rate']
            rate *= rate2
        return {'rate': rate, 'amount': None}

    @classmethod
    def orders(cls, api, market, orderType, depth=LIMIT):
        data = cls.__get_orders(api, market)
        orders = []
        if data is None:
            return None
        if 'result' in data:
            data = data['result']
        offers = data[ORDERS_OPTION[api][orderType]]
        for offer in offers[:depth]:
            order = {'rate': float(offer[ORDERS_OPTION[api]['rate']]),
                     'amount': float(offer[ORDERS_OPTION[api]['amount']])}
            orders.append(order)
        return orders

    @classmethod
    def __get_bittrex_transfer_fees(cls):
        result = dict()
        respond = cls.__data_request(TRANSFER_FEES[BITTREX])
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
        response = cls.__data_request(URL[BITTREX]['markets'])
        result = []
        if not(response is None):
            for market in response.json():
                result.append(market['symbol'])
        return result

    @classmethod
    def __get_bitbay_markets(cls):
        response = cls.__data_request(URL[BITBAY]['markets'])
        result = []
        data = response.json()['items'].keys()
        if not(response is None):
            for market in data:
                result.append(market)
        return result

    @classmethod
    def __get_orders(cls, api, market):
        if not(api in URL):
            print('unknown API')
            return None
        if URL[api]['markets'] is None:
            return None
        url = URL[api]['orders'] + market + URL[api]['suffix']
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
    def __data_request(url, headers=None, querystring=None):
        if headers is None and querystring is None:
            response = requests.get(url)
        else:
            response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code != 200:
            print(response.text)
            return None
        else:
            return response


if __name__ == '__main__':
    api1 = Api()
    data1 = api1.last_rate(STOOQ, 'CDR-PLN')
    print(data1['rate'])
    data2 = api1.last_rate(YAHOO, 'TSLA-PLN')
    print(data2['rate'])
    data3 = api1.last_rate(NBP, 'USD-PLN')
    print(data3['rate'])
