import pandas
from itertools import permutations
import json
import lab4

API_SHORT_NAME = {'bitbay': "BB", 'bittrex': 'BITT'}

API = {'cryptocurrencies': {
            'bitbay': {'request': ['orderbook', 'market', 'ticker', 'all'],
                       'path': 'https://bitbay.net/API/Public/', 'format': 'json',
                       'markets_path': 'https://api.bitbay.net/rest/trading/ticker',
                       'market_currencies': 'items'},
            'bittrex': {'request': ['orderbook', 'ticker'],
                        'path': 'https://api.bittrex.com/v3/markets', 'format': 'depth=25',
                        'markets_path': 'https://api.bittrex.com/v3/markets',
                        'market_currencies': 'symbol'}},
       'stocks': {
           'eodhistoricaldata': {'path': 'https://eodhistoricaldata.com/api',
                                 'request': ['real-time', 'eod'],
                                 'format': 'json', 'api_key_file': 'api_key.json'}},
       'currencies': {
           'nbp': {'path': 'http://api.nbp.pl/api/exchangerates',
                   'request': ['tables/A'],
                   'format': 'json', 'today': 'today'}}
       }
EOD_HIST = 'eodhistoricaldata'
NBP = 'nbp'
PROFIT_TAX = 0.19


def get_api_path(api, request_type, stock_NASDAQ_code=None):
    if api == EOD_HIST and request_type == 'real-time' and stock_NASDAQ_code is not None:
        stock = API['stocks'][api]
        with open(stock['api_key_file'], 'r') as key_file:
            key = json.load(key_file)
        if key is not None:
            return str('{0}/{1}/{2}?api_token={3}&fmt={4}'.format(stock['path'],
                                                                  request_type, stock_NASDAQ_code,
                                                                  key['api_key'], stock['format']))
    if api == NBP and request_type == API['currencies'][api]['request'][0]:
        api_data = API['currencies'][api]
        return str('{0}/{1}/{2}/?format={3}'.format(api_data['path'], request_type,
                                                    api_data['today'], api_data['format']))


def get_multiple_stocks_path(stock_api, stock_NASDAQ):
    if stock_api == EOD_HIST and \
            stock_NASDAQ is not None and len(stock_NASDAQ) > 1:
        path = get_api_path(stock_api, 'real-time', stock_NASDAQ[0])
        path += '&s='
        for nbr in range(1, len(stock_NASDAQ)):
            path += str('{0}'.format(stock_NASDAQ[nbr]))
            if nbr < len(stock_NASDAQ) - 1:
                path += ','
        return path


class Investment:
    def __init__(self, wallet_file_name):
        self.__wallet = self.read_wallet(wallet_file_name)
        self.__cryptocurrencies = self.__wallet['resources']['cryptocurrencies']
        self.__currencies = self.__wallet['resources']['currencies']
        self.__polish_stocks = self.__wallet['resources']['polish stocks']
        self.__foreign_stocks = self.__wallet['resources']['foreign stocks']
        self.__rates = Investment.get_exchange_table()

    @staticmethod
    def read_wallet(file_name):
        with open(file_name, 'r') as file:
            wallet = json.load(file)
        return wallet

    @staticmethod
    def get_exchange_table():
        response = lab4.get_response(get_api_path(NBP, API['currencies'][NBP]['request'][0]))
        if response is not None:
            rates = response.json()
            return rates[0]['rates']

    def get_exchange_rate(self, currency_from, currency_to):
        rate_to_pln, rate_from_pln = 1, 1
        for rate in self.__rates:
            if rate['code'] == currency_from:
                rate_to_pln = rate['mid']
            if currency_to != 'PLN' and rate['code'] == currency_to:
                rate_from_pln = rate['mid']
        if currency_to == 'PLN':
            return rate_to_pln
        else:
            return rate_to_pln / rate_from_pln

    def sell_currencies(self, percent=100):
        result = {}
        for currency in self.__currencies.keys():
            if currency not in result:
                amount = self.__currencies[currency]['amount'] * percent / 100
                ratio = self.get_exchange_rate(currency, self.__wallet['base currency'])
                gain = amount * ratio
                result[currency] = {'amount': amount, 'rate': ratio, 'gain': gain,
                                    'netto': Investment.count_netto_value(gain,
                                                                          self.__currencies[currency][
                                                                              'average price'] * amount)}
        return result

    def get_stocks_responses(self):
        responses = {}
        for stock in {**self.__foreign_stocks, **self.__polish_stocks}:
            if stock is not None and stock not in responses:
                resp = lab4.get_response(get_api_path(EOD_HIST, 'real-time', stock))
                if resp is not None:
                    responses[stock] = resp.json()
        return responses

    def sell_stocks(self, api_responses, percent=100):
        stock_sold = {}
        for stock in {**self.__foreign_stocks, **self.__polish_stocks}:
            if stock is not None and stock not in stock_sold:
                stock_sold[stock] = self.sell_stock(stock, api_responses[stock], percent)
        return stock_sold

    def sell_stock(self, stock_name, api_response, percent=100):
        stock = None
        if stock_name in self.__polish_stocks:
            stock = self.__polish_stocks[stock_name]
        elif stock_name in self.__foreign_stocks:
            stock = self.__foreign_stocks[stock_name]
        if stock is not None and api_response['code'] == stock_name:
            amount = stock['amount'] * percent / 100
            if api_response['close'] != 'NA':
                rate = api_response['close']
            else:
                rate = api_response['previousClose']
            gain = amount * rate
            if stock['currency'] != self.__wallet['base currency']:
                ratio = self.get_exchange_rate(stock['currency'], self.__wallet['base currency'])
                gain = gain * ratio
            return {'name': stock_name, 'amount': amount, 'rate': rate, 'gain': gain,
                    'netto': Investment.count_netto_value(gain, stock['average price'] * amount)}

    def sell_cryptocurrencies(self, crypto_responses, percent=100):
        sold = {}
        for response in crypto_responses:
            currency = response.get_currency_in
            amount_to_sell = (self.__cryptocurrencies[currency]['amount'] * percent) / 10
            sold[currency] = self.sell_cryptocurrency(currency, amount_to_sell, response)
        return sold

    def get_cryptocurrencies_responses(self, api):
        responses = []
        for pair in lab4.get_markets(api):
            if pair[1] == self.__wallet['base currency']:
                for currency in self.__cryptocurrencies.keys():
                    if pair[0] == currency:
                        responses.append(lab4.ApiResponse(pair[0], pair[1], api))
        return responses

    def sell_cryptocurrency(self, currency_sell, amount, api_response):
        resp = api_response
        rate, amount_sold, offer_nbr, last_rate, gain = 0, 0, 0, 0, 0
        max_offer_nbr = resp.get_offer_number - 2
        offer = resp.get_offer(offer_nbr)
        cont_selling = True
        transactions = []
        while cont_selling:
            transaction = offer['sell']
            last_rate = transaction[lab4.RATE]
            transact_amount = transaction[lab4.AMOUNT]
            if amount - amount_sold > transact_amount:
                gain += transact_amount * last_rate
                amount_sold += transact_amount
                transactions.append({'offer_nbr': offer_nbr, 'offer': transaction, 'amount': transact_amount})
                if offer_nbr < max_offer_nbr:
                    offer_nbr += 1
                    offer = resp.get_offer(offer_nbr)
                else:
                    cont_selling = False
            elif amount - amount_sold <= transact_amount:
                cont_selling = False
                gain += (amount - amount_sold) * last_rate
                amount_sold = amount
                transactions.append({'offer_nbr': offer_nbr, 'offer': transaction, 'amount': (amount - amount_sold)})
        return {'currency_sold': currency_sell, 'amount': amount_sold, 'rate': last_rate, 'gain': gain,
                'netto': Investment.count_netto_value(
                    gain, self.__cryptocurrencies[currency_sell]['average price'] * amount_sold),
                'transactions': transactions}

    @staticmethod
    def count_netto_value(gain, payed):
        profit = gain - payed
        if profit > 0:
            tax = profit * PROFIT_TAX
            return gain - tax
        return gain

    def get_most_profitable_sells(self, crypto_responses, percent=100):
        api_sells = {}
        for api in lab4.APIs:
            api_sells[api] = self.sell_cryptocurrencies(crypto_responses[api], percent)
        sold = {}
        for api in api_sells.keys():
            for currency in api_sells[api].keys():
                if currency in sold:
                    if sold[currency]['gain'] < api_sells[api][currency]['gain']:
                        sold[currency] = {**api_sells[api][currency], **{'api': api}}
                else:
                    sold[currency] = {**api_sells[api][currency], **{'api': api}}
        return sold

    def get_all_api_responses(self):
        responses = {}
        for api in lab4.APIs:
            responses[api] = self.get_cryptocurrencies_responses(api)
        return responses

    def get_arbitrage_offers(self, api_in, api_out):
        if api_in in lab4.APIs and api_out in lab4.APIs:
            arbitrage = {}
            markets = lab4.get_common_markets(api_in, api_out)
            for currency in self.__cryptocurrencies:
                for pair in markets:
                    if currency == pair[0]:
                        arbitrage[pair] = lab4.count_arbitrage(currency, pair[1], api_in, api_out, fees_on=True)
            return arbitrage

    def get_all_api_arbitrage(self):
        api_pairs = permutations(lab4.APIs, 2)
        result = {}
        for pair in api_pairs:
            result[pair] = self.get_arbitrage_offers(pair[0], pair[1])
        return result

    def profitable_arbitrage(self):
        arbitrage = self.get_all_api_arbitrage()
        profitable_arb = {}
        for api_pair in arbitrage.keys():
            if api_pair[0] in API_SHORT_NAME and api_pair[1] in API_SHORT_NAME:
                names = API_SHORT_NAME[api_pair[0]], API_SHORT_NAME[api_pair[1]]
            else:
                names = api_pair
            for offer in arbitrage[api_pair].values():
                if offer['profit'] > 0:
                    if offer['currencies'][0] not in profitable_arb:
                        profitable_arb[offer['currencies'][0]] = ""
                    profitable_arb[offer['currencies'][0]] += \
                        "{0[0]}-{0[1]}, {1[0]} {1[1]}, +{2}{1[0]} ".format(names, offer['currencies'], offer['profit'])
            for crypto in self.__cryptocurrencies:
                if crypto not in profitable_arb:
                    profitable_arb[crypto] = 'non profitable offers'
        return profitable_arb

    @staticmethod
    def get_list(all_value, ten_percent, api, arbitrage=None):
        result = []
        for item in all_value:
            if api is None:
                api = all_value[item]['api']
                arbitrage = arbitrage[item]
            else:
                arbitrage = ''
            result.append([item, all_value[item]['amount'],
                           all_value[item]['rate'], all_value[item]['gain'],
                           all_value[item]['netto'], api,
                           ten_percent[item]['gain'], ten_percent[item]['netto'],
                           api, arbitrage])
        return result

    def data_frame_sell_resources(self):
        columns = ['name', 'amount', 'rate', 'value', 'value netto', 'api',
                   'value 10%', 'value netto 10%', 'api 10%', 'arbitrage']
        crypto_resp = self.get_all_api_responses()
        crypto = Investment.get_list(self.get_most_profitable_sells(crypto_resp),
                                     self.get_most_profitable_sells(crypto_resp, 10), None, self.profitable_arbitrage())
        # stock_resp = self.get_stocks_responses()
        # stocks = Investment.get_list(self.sell_stocks(stock_resp),
        #                              self.sell_stocks(stock_resp, 10), EOD_HIST)
        currencies = Investment.get_list(self.sell_currencies(), self.sell_currencies(10), NBP)
        table = crypto + currencies
        # + stocks
        df = pandas.DataFrame(data=table, columns=columns)
        return df


if __name__ == '__main__':
    inv = Investment('wallet.json')
    print(inv.data_frame_sell_resources().to_string())
