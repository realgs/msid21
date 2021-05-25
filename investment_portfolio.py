import json
from enum import Enum
from multiprocessing import Pool

import pandas as pd
import requests

from Studia.MSiD.lab4 import task1_2_3
from Studia.MSiD.lab4.task1_2_3 import ADDRESSES, DATA_CONST, SELL, FEES, TAKER, BITBAY, BITTREX, ORDERBOOK, RATE

NBP = 'NBP'
EODDATA = 'eodhistoricaldata'
GAIN_TAX = 0.19
ONE_MARKET = 'One_market'
MULTIPLE_MARKETS_SUFFIX = 'Multiple_market_suffix'
ROUNDING = 4
QUANTITY = 'QUANTITY'
CURRENCY = 'CURRENCY'
PRICE = 'PRICE'
NAME = 'NAME'
RESOURCES = 'RESOURCES'
BASE_CURRENCY = 'BASE_CURRENCY'
DEFAULT_CONF_FILE = 'default.json'

ADDRESSES_LOCAL = {NBP: 'http://api.nbp.pl/api/exchangerates/tables/A/?format=json',
                   EODDATA: {ONE_MARKET: 'https://eodhistoricaldata.com/api/real-time/{1}?api_token={0}&fmt=json',
                             MULTIPLE_MARKETS_SUFFIX: '&s={}'}}
task1_2_3.ADDRESSES.update(ADDRESSES_LOCAL)
SELL_CONST = {RESOURCES: 'resources', NAME: 'name', QUANTITY: 'quantity', PRICE: 'price',
              CURRENCY: 'currency', BASE_CURRENCY: 'base_currency'}


class StockType(Enum):
    POLISH = "polish stock"
    FOREIGN = "foreign stock"


def get_first_currency(market):
    return market.split("-")[0]


def get_resources(file_name):
    try:
        with open(file_name, 'r') as to_load:
            json_data = json.load(to_load)
            return json_data
    except FileNotFoundError:
        print('file {} not found'.format(file_name))


def get_convert_table():
    try:
        response = requests.get(ADDRESSES[NBP])
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Connection to api failed")
        return None


def get_stock_markets_json(file_name, markets_list):
    key_json = get_resources(file_name)
    if key_json:
        key = key_json["key"]
        address = ADDRESSES[EODDATA][ONE_MARKET].format(key, markets_list[0])
        if len(markets_list) > 1:
            markets_string = change_list_form(markets_list[1:])
            address += ADDRESSES[EODDATA][MULTIPLE_MARKETS_SUFFIX].format(markets_string)
        try:
            response = requests.get(address)
            return response.json()
        except requests.exceptions.ConnectionError:
            print("Connection to api failed")
            return None
    else:
        return None


def change_list_form(markets_list):
    result = ''
    for market in markets_list[:-1]:
        result += str(market) + ','
    result += str(markets_list[-1])
    return result


def get_gain_tax(quantity, price, value):
    gain = value - quantity * price
    if gain > 0:
        return gain * GAIN_TAX
    else:
        return 0.0


class Portfolio(object):
    def __init__(self, file_name):
        json_data = get_resources(file_name)
        if not json_data:
            json_data = get_resources(DEFAULT_CONF_FILE)
        self.resources = json_data[SELL_CONST[RESOURCES]]
        self.base_currency = json_data[SELL_CONST[BASE_CURRENCY]]
        self.bittrex_markets, self.bitbay_markets = task1_2_3.get_markets()
        self.convert_table = get_convert_table()

    def convert_ratio_currency(self, from_curr, to_curr):
        result_ratio = 0
        if self.convert_table:
            if from_curr == 'PLN' or to_curr == 'PLN':
                for elem in self.convert_table[0]['rates']:
                    if elem['code'] == to_curr:
                        mid = elem['mid']
                        result_ratio = 1 / mid
                    elif elem['code'] == from_curr:
                        mid = elem['mid']
                        result_ratio = mid
            else:
                result_ratio = \
                    self.convert_ratio_currency(from_curr, 'PLN') * \
                    self.convert_ratio_currency('PLN', to_curr)
        return result_ratio

    def make_data_frame(self, percent=30):
        per_name = 'value {}%'.format(percent)
        netto_per_name = 'netto value {}%'.format(percent)
        columns = ['name', 'quantity', 'rate', 'value', 'netto value', 'api',
                   per_name, netto_per_name, 'per api', 'arbitrage', 'base currency']
        table = []
        table_sums = [0, 0, 0, 0]
        crypto_sell_data = self.sell_crypto_currencies(percent)
        crypto_arbitrage = self.get_arbitrage()
        table, table_sums = self.write_to_table(percent, table, table_sums, crypto_sell_data, crypto_arbitrage)

        currencies_sell_data = self.sell_currencies(percent)
        table, table_sums = self.write_to_table(percent, table, table_sums, currencies_sell_data)

        pol_st_sell_data = self.sell_stocks(StockType.POLISH.value, percent)
        table, table_sums = self.write_to_table(percent, table, table_sums, pol_st_sell_data)

        for_st_sell_data = self.sell_stocks(StockType.FOREIGN.value, percent)
        table, table_sums = self.write_to_table(percent, table, table_sums, for_st_sell_data)

        table.append(['Sum', '', '', round(table_sums[0], ROUNDING),
                      round(table_sums[1], ROUNDING), '',
                      round(table_sums[2], ROUNDING), round(table_sums[3], ROUNDING),
                      '', 'not applicable', self.base_currency])
        df = pd.DataFrame(columns=columns, data=table)
        return df

    @staticmethod
    def add_sums(table_sums, sums):
        for i in range(0, len(table_sums)):
            table_sums[i] += sums[i]
        return table_sums

    def write_to_table(self, percent, table, table_sums, sell_data, arbitrage_dict=None):
        value_sum, value_netto_sum, per_value_sum, per_value_netto_sum = 0, 0, 0, 0
        per_name = 'value {}%'.format(percent)
        netto_per_name = 'netto value {}%'.format(percent)
        arbitrage = 'not applicable'
        for key in sell_data.keys():
            if arbitrage_dict:
                arbitrage = arbitrage_dict[key]

            value = sell_data[key]['value']
            per_value = sell_data[key][per_name]
            value_netto = sell_data[key]['netto value']
            per_value_netto = sell_data[key][netto_per_name]
            value_sum += value
            value_netto_sum += value_netto
            per_value_sum += per_value
            per_value_netto_sum += per_value_netto

            table.append([key, sell_data[key]['quantity'], round(sell_data[key]['rate'], ROUNDING),
                          round(value, ROUNDING), round(value_netto, ROUNDING), sell_data[key]['api'],
                          round(per_value, ROUNDING), round(per_value_netto, ROUNDING),
                          sell_data[key]['per api'], arbitrage, self.base_currency])
        table_sums = self.add_sums(table_sums, [value_sum, value_netto_sum, per_value_sum, per_value_netto_sum])
        return table, table_sums

    def sell_currencies(self, percent):
        currencies_dict = self.resources["currencies"]
        sell_dict = {}
        for elem in currencies_dict:
            market, price, quantity, per_quantity, currency = self.data_as_float(elem, percent, False)
            if currency != self.base_currency:
                price = price * self.convert_ratio_currency(currency, self.base_currency)
            rate = self.convert_ratio_currency(market, self.base_currency)
            value = rate * quantity
            per_value = rate * per_quantity
            per_name, netto_per_name, netto_value, per_netto_value = \
                self.get_netto_value_names(percent, price, quantity, value, per_quantity, per_value)
            api = 'NBP'

            sell_dict[market] = {'quantity': quantity, 'rate': rate, 'value': value,
                                 'netto value': netto_value, 'api': api, per_name: per_value,
                                 netto_per_name: per_netto_value, 'per api': api}
        return sell_dict

    def sell_stocks(self, stock_type, percent):
        stocks_dict = self.resources[stock_type]
        sell_dict = {}
        for elem in stocks_dict:
            ratio = 1
            market, price, quantity, per_quantity, currency = self.data_as_float(elem, percent, False)
            if currency != self.base_currency:
                ratio = self.convert_ratio_currency(currency, self.base_currency)
                price = price * ratio
            response = get_stock_markets_json('api_key.json', [market])
            if response:
                close = response['close']
                if close == 'NA':
                    rate = response['previousClose']
                else:
                    rate = close
                if currency != self.base_currency and ratio:
                    rate = rate * ratio
                value = rate * quantity
                per_value = rate * per_quantity
                per_name, netto_per_name, netto_value, per_netto_value = \
                    self.get_netto_value_names(percent, price, quantity, value, per_quantity, per_value)
                api = 'EOD'

                sell_dict[market] = {'quantity': quantity, 'rate': rate, 'value': value,
                                     'netto value': netto_value, 'api': api, per_name: per_value,
                                     netto_per_name: per_netto_value, 'per api': api}
        return sell_dict

    @staticmethod
    def get_netto_value_names(percent, price, quantity, value, per_quantity, per_value):
        per_name = 'value {}%'.format(percent)
        netto_per_name = 'netto value {}%'.format(percent)
        netto_value = value - get_gain_tax(quantity, price, value)
        per_netto_value = per_value - get_gain_tax(per_quantity, price, per_value)
        return per_name, netto_per_name, netto_value, per_netto_value

    def sell_crypto_currencies(self, percent=30):
        crypto_currencies_dict = self.resources['crypto_currencies']
        sell_dict = {}
        sell_bitbay = {}
        sell_bittrex = {}
        with Pool(processes=4) as pool:
            for elem in crypto_currencies_dict:
                market, price, quantity, per_quantity, currency = self.data_as_float(elem, percent, True)
                response_bitbay, response_bittrex = None, None

                if self.bitbay_markets and market in self.bitbay_markets:
                    response_bitbay = task1_2_3.get_json(BITBAY, ORDERBOOK, market)
                if self.bittrex_markets and market in self.bittrex_markets:
                    response_bittrex = task1_2_3.get_json(BITTREX, ORDERBOOK, market)

                sell_bitbay[market] = pool.apply_async(
                    self.sell_crypto_currencies_on_api,
                    args=[quantity, per_quantity, response_bitbay, BITBAY])
                sell_bittrex[market] = pool.apply_async(
                    self.sell_crypto_currencies_on_api,
                    args=[quantity, per_quantity, response_bittrex, BITTREX])

            for elem in crypto_currencies_dict:
                market, price, quantity, per_quantity, currency = self.data_as_float(elem, percent, True)
                if currency != self.base_currency:
                    price = price * self.convert_ratio_currency(currency, self.base_currency)
                value_bitbay, rate_bitbay, per_value_bitbay, per_rate_bitbay = sell_bitbay[market].get()
                value_bittrex, rate_bittrex, per_value_bittrex, per_rate_bittrex = sell_bittrex[market].get()

                value, rate, api = \
                    self.get_best_api(value_bitbay, rate_bitbay, BITBAY, value_bittrex,
                                      rate_bittrex, BITTREX)
                per_value, per_rate, per_api = \
                    self.get_best_api(per_value_bitbay, per_rate_bitbay, BITBAY, per_value_bittrex,
                                      per_rate_bittrex, BITTREX)

                per_name, netto_per_name, netto_value, per_netto_value = \
                    self.get_netto_value_names(percent, price, quantity, value, per_quantity, per_value)

                sell_dict[elem[SELL_CONST[NAME]]] = {'quantity': quantity, 'rate': rate, 'value': value,
                                                     'netto value': netto_value, 'api': api, per_name: per_value,
                                                     netto_per_name: per_netto_value, 'per api': per_api}
        return sell_dict

    @staticmethod
    def data_as_float(elem, percent, is_cryptocurrency):
        currency = elem[SELL_CONST[CURRENCY]]
        if is_cryptocurrency:
            name = elem[SELL_CONST[NAME]] + '-' + currency
        else:
            name = elem[SELL_CONST[NAME]]
        return name, float(elem[SELL_CONST[PRICE]]), float(elem[SELL_CONST[QUANTITY]]), \
               float(elem[SELL_CONST[QUANTITY]]) * percent / 100.0, currency

    def sell_crypto_currencies_on_api(self, quantity, per_quantity, response, api):
        if response is not None:
            value, rate = \
                self.sell_crypto_currency_rec(quantity, response, api, 0)
            per_value, per_rate = \
                self.sell_crypto_currency_rec(per_quantity, response, api, 0)
            return value, rate, per_value, per_rate
        else:
            return 0, 0, 0, 0

    @staticmethod
    def get_best_api(value_1, rate_1, api_1, value_2, rate_2, api_2):
        value, rate, api = max((value_1, rate_1, api_1),
                               (value_2, rate_2, api_2))
        return value, rate, api

    def sell_crypto_currency_rec(self, quantity, response, fee_source, sell_offer_number):
        value, sell_quantity, sell_rate = self.sell_crypto_currency(quantity, response,
                                                                    fee_source, sell_offer_number)
        rest_quantity = quantity - sell_quantity
        if rest_quantity > 0:
            part_value, sell_rate = self.sell_crypto_currency_rec(rest_quantity, response,
                                                                  fee_source, sell_offer_number + 1)
            value += part_value
        return value, sell_rate

    @staticmethod
    def sell_crypto_currency(quantity, response, fee_source, sell_offer_number):
        sell_quantity = float(task1_2_3.get_data(response, DATA_CONST[fee_source][SELL],
                                                 DATA_CONST[fee_source][QUANTITY], sell_offer_number))
        sell_rate = float(task1_2_3.get_data(response, DATA_CONST[fee_source][SELL],
                                             DATA_CONST[fee_source][RATE], sell_offer_number))
        sell_quantity = min(sell_quantity, quantity)
        value = task1_2_3.get_profit(sell_rate, sell_quantity, FEES[fee_source][TAKER], 0, True)
        return value, sell_quantity, sell_rate

    def get_arbitrage(self):
        arbitrage_dict = {}
        markets_list = self.get_portfolio_markets_list()

        markets_dict_bittrex_bitbay, markets_dict_bitbay_bittrex = task1_2_3.get_arbitrage_for_markets(markets_list,
                                                                                                       True, True)
        for market in markets_list:
            crypto_currency = get_first_currency(market)
            if crypto_currency not in arbitrage_dict:
                arbitrage_dict[crypto_currency] = []

            bitt_bb_string = self.get_arbitrage_inscription(crypto_currency, market,
                                                            markets_dict_bittrex_bitbay, 'BITT-BB')
            bb_bitt_string = self.get_arbitrage_inscription(crypto_currency, market,
                                                            markets_dict_bitbay_bittrex, 'BB-BITT')
            if bitt_bb_string:
                arbitrage_dict[crypto_currency].append(bitt_bb_string)
            if bb_bitt_string:
                arbitrage_dict[crypto_currency].append(bb_bitt_string)
        return arbitrage_dict

    def get_portfolio_markets_list(self):
        crypto_currencies_dict = self.resources['crypto_currencies']
        currencies_list = []
        markets_list = []
        common_markets_list = task1_2_3.get_common_markets(self.bittrex_markets, self.bitbay_markets)
        for elem in crypto_currencies_dict:
            currencies_list.append(elem['name'])

        if common_markets_list:
            for market in common_markets_list:
                in_currency = get_first_currency(market)
                if in_currency in currencies_list:
                    markets_list.append(market)
        return markets_list

    @staticmethod
    def get_arbitrage_inscription(crypto_currency, market, markets_dict, apis_string):
        if markets_dict and market in markets_dict:
            earn = markets_dict[market][0]['earn']
            if earn > 0:
                arbitrage_string = '{0}, {1}, +{2} {3}'.format(
                    apis_string, market, earn, crypto_currency)
                return arbitrage_string
        else:
            return None


def main():
    port = Portfolio('conf.json')
    print(port.make_data_frame().to_string())


if __name__ == '__main__':
    main()
