import pandas
from itertools import permutations
import json
import lab4
API_SHORT_NAME = {'bitbay': "BB", 'bittrex': 'BITT'}

API = {'cryptocurrencies':
           {'bitbay': {'request': ['orderbook', 'market', 'ticker', 'all'],
                       'path': 'https://bitbay.net/API/Public/', 'format': 'json',
                       'markets_path': 'https://api.bitbay.net/rest/trading/ticker',
                       'market_currencies': 'items'},
            'bittrex': {'request': ['orderbook', 'ticker'],
                        'path': 'https://api.bittrex.com/v3/markets', 'format': 'depth=25',
                        'markets_path': 'https://api.bittrex.com/v3/markets',
                        'market_currencies': 'symbol'}},
       'currencies': {}
       }
PROFIT_TAX = 0.19


class Investment:
    def __init__(self, wallet_file_name):
        self.__wallet = self.read_wallet(wallet_file_name)
        self.__cryptocurrencies = self.__wallet['resources']['cryptocurrencies']
        self.__currencies = self.__wallet['resources']['currencies']

    @staticmethod
    def read_wallet(file_name):
        with open(file_name, 'r') as file:
            wallet = json.load(file)
        return wallet

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
                'netto': self.count_netto_value(currency_sell, amount_sold, gain), 'transactions': transactions}

    def count_netto_value(self, crypto, amount_to_sell, gain):
        if crypto in self.__cryptocurrencies:
            profit = gain - self.__cryptocurrencies[crypto]['average price'] * amount_to_sell
            if profit > 0:
                profit = profit * (1-PROFIT_TAX)
            return profit

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


    def data_frame_sell_resources(self):
        columns = ['name', 'amount', 'rate', 'value', 'value netto', 'api', 'value 10%', 'value netto 10%', 'api 10%', 'arbitrage']
        all_resp = self.get_all_api_responses()
        cryptocurrencies = self.get_most_profitable_sells(all_resp)
        crypto_ten_percent = self.get_most_profitable_sells(all_resp, 5)
        arbitrage = self.profitable_arbitrage()
        table = []
        for crypto in cryptocurrencies.keys():
            table.append([crypto, cryptocurrencies[crypto]['amount'],
                          cryptocurrencies[crypto]['rate'], cryptocurrencies[crypto]['gain'],
                          cryptocurrencies[crypto]['netto'], cryptocurrencies[crypto]['api'],
                          crypto_ten_percent[crypto]['gain'], crypto_ten_percent[crypto]['netto'],
                          crypto_ten_percent[crypto]['api'], arbitrage[crypto]])
        df = pandas.DataFrame(data=table, columns=columns)
        return df


if __name__ == '__main__':
    inv = Investment('wallet.json')
    print(inv.data_frame_sell_resources().to_string())



