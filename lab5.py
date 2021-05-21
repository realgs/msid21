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
WALLET_ERRORS = ['OK', 'category', 'amount', 'avr price', 'currency']


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
        self.__file_name = wallet_file_name
        self.__wallet = self.read_wallet(wallet_file_name)
        self.__cryptocurrencies = self.__wallet['resources']['cryptocurrencies']
        self.__currencies = self.__wallet['resources']['currencies']
        self.__polish_stocks = self.__wallet['resources']['polish stocks']
        self.__foreign_stocks = self.__wallet['resources']['foreign stocks']
        self.__rates = Investment.get_exchange_table()

    @property
    def base_currency(self):
        return self.__wallet['base currency']

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
        else:
            return None

    def get_exchange_rate(self, currency_from, currency_to):
        rate_to_pln, rate_from_pln = 1, 1
        if self.__rates is None:
            return 1
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
                else:
                    return None
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
                        api_resp = lab4.ApiResponse(pair[0], pair[1], api)
                        if api_resp is not None:
                            responses.append(api_resp)
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
    def get_list(all_value, percent, api, arbitrages=None):
        result = []
        sum_of = [0, 0, 0, 0]
        for item in all_value:
            if api is None:
                api = all_value[item]['api']
            if arbitrages is not None:
                arbitrage = arbitrages[item]
            else:
                arbitrage = ''
            sum_of[0] += all_value[item]['gain']
            sum_of[1] += all_value[item]['netto']
            sum_of[2] += percent[item]['gain']
            sum_of[3] += percent[item]['netto']
            result.append([item, all_value[item]['amount'],
                           all_value[item]['rate'], all_value[item]['gain'],
                           all_value[item]['netto'], api,
                           percent[item]['gain'], percent[item]['netto'],
                           api, arbitrage])
        return [result, sum_of]

    def data_frame_sell_resources(self, percent):
        value = 'value {0}%'.format(percent)
        value_netto = 'value netto {0}%'.format(percent)
        api_p = 'api {}%'.format(percent)
        columns = ['name', 'amount', 'rate', 'value', 'value netto', 'api',
                   value, value_netto, api_p, 'arbitrage']
        crypto_resp = self.get_all_api_responses()
        sum_of = [0, 0, 0, 0]
        crypto, currencies, stocks = None, None, None
        to_table = []
        if len(crypto_resp) > 0:
            crypto_all = Investment.get_list(self.get_most_profitable_sells(crypto_resp),
                                             self.get_most_profitable_sells(crypto_resp, percent),
                                             None, self.profitable_arbitrage())
            to_table.append(crypto_all[0])
            sum_of = crypto_all[1]
        stock_resp = self.get_stocks_responses()
        if stock_resp is not None:
            stocks_all = Investment.get_list(self.sell_stocks(stock_resp),
                                             self.sell_stocks(stock_resp, percent), EOD_HIST)
            to_table.append(stocks_all[0])
        if self.__rates is not None:
            currencies_all = Investment.get_list(self.sell_currencies(), self.sell_currencies(percent), NBP)
            to_table.append(currencies_all[0])
        for nbr in range(len(sum_of)):
            if currencies is not None:
                sum_of[nbr] += currencies_all[1][nbr]
            if stocks is not None:
                sum_of[nbr] += stocks_all[1][nbr]
        table = []
        for item in to_table:
            table += item
        table.append(['SUM', '', '', sum_of[0], sum_of[1], '', sum_of[2], sum_of[3], '', ''])
        df = pandas.DataFrame(data=table, columns=columns)
        return df

    def add_to_wallet_file(self, category, name, amount, avr_price, currency_buy):
        """
            error codes:
            0 - no errors
            1 - category error
            2 - amount error
            3 - avr_price error
            4 - currency_buy error
        """
        if type(amount) != float and type(amount) != int:
            return 2
        elif type(avr_price) != float and type(avr_price) != int:
            return 3
        wallet_dict = self.__wallet
        categories = list(self.__wallet['resources'].keys())
        resources = self.__wallet['resources']
        stocks = ['polish stocks', 'foreign stocks']
        ratio = 1
        if currency_buy != self.__wallet['base currency'] and category not in stocks:
            ratio = self.get_exchange_rate(currency_buy, self.__wallet['base currency'])
        if category in categories:
            if name in resources[category]:
                wallet_dict['resources'][category][name]['amount'] += amount
                rate = resources[name]['average price']
                amount_in = resources[category]['amount']
                wallet_dict['resources'][category][name]['average price'] = \
                    (avr_price * ratio * amount + rate * amount_in) / (amount + amount_in)
                if name in stocks and currency_buy != resources[category][name]['currency']:
                    return 4
            else:
                wallet_dict['resources'][category][name] = {'amount': amount, 'average price': avr_price * ratio}
                if category in stocks:
                    print(name)
                    wallet_dict['resources'][category][name] = {**wallet_dict['resources'][category][name],
                                                                **{'currency': currency_buy}}
        else:
            return 1
        with open(self.__file_name, 'w') as file:
            json.dump(wallet_dict, file)
        return 0


if __name__ == '__main__':
    inv = Investment('wallet.json')
    print(inv.data_frame_sell_resources(20).to_string())
