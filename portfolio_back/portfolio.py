import json
from threading import Thread

import pandas as pd

from portfolio_back.data_retriever import DataRetriever

POLISH_STOCK_EXCHAGE_SYMBOL = '.WAR'

TAX_RATIO = .19
DEPTH = 25
DEFAULT_CURRENCY = 'USD'
POLISH_CURRENCY = 'PLN'


class Asset:

    def __init__(self, price, volume, name, base_currency):
        self.price = price
        self.volume = volume
        self.name = name
        self.base_currency = base_currency

    def __repr__(self):
        return f"{self.volume} {self.name} for price: {self.price}{self.base_currency}"


class Wallet:

    def __init__(self, wallet_dict):
        self.base_currency = wallet_dict['base currency']
        self.currencies = wallet_dict['assets']['currencies']
        self.cryptocurrencies = wallet_dict['assets']['cryptocurrencies']
        self.shares = wallet_dict['assets']['shares']
        self.data_retriever = DataRetriever()
        self.default_to_base_currency = \
            self.data_retriever.get_exchange_rate(DEFAULT_CURRENCY,
                                                  self.base_currency) if self.base_currency != DEFAULT_CURRENCY else 1
        self.zloty_to_default_currency = \
            self.data_retriever.get_exchange_rate(POLISH_CURRENCY, DEFAULT_CURRENCY)

    @classmethod
    def wallet_from_json(cls, wallet_path):
        wallet_dict = Wallet.read_wallet(wallet_path)
        return cls(wallet_dict)

    @classmethod
    def empty_wallet(cls):
        wallet_dict = {
            'base currency': DEFAULT_CURRENCY,
            'assets': {
                'currencies': [],
                'cryptocurrencies': [],
                'shares': [],
            }
        }
        return cls(wallet_dict)

    @staticmethod
    def read_wallet(wallet_path):
        with open(wallet_path, 'r') as f:
            temp_wallet = json.load(f)
        return temp_wallet

    def convert_default_to_base_currency(self, amount):
        return amount * self.default_to_base_currency

    def convert_zloty_to_default_currency(self, amount):
        return amount * self.zloty_to_default_currency

    def change_base_currency(self, currency):
        current_to_new = self.data_retriever.get_exchange_rate(self.base_currency, currency)
        self.base_currency = currency
        self.default_to_base_currency = \
            self.data_retriever.get_exchange_rate(DEFAULT_CURRENCY,
                                                  self.base_currency) if self.base_currency != DEFAULT_CURRENCY else 1
        for asset_type in [self.cryptocurrencies, self.currencies, self.shares]:
            for item in asset_type:
                for buy in item['buy history']:
                    buy['buy price'] *= current_to_new

    @staticmethod
    def calculate_net(buy_history, sell_price, percentage=1, tax=TAX_RATIO):
        sum_net = 0

        for buy in buy_history:
            gross = (buy['volume'] * percentage) * (sell_price - buy['buy price'])
            sum_net += gross if gross <= 0 else (1 - tax) * gross

        return sum_net

    def get_complete_assets_dataframe(self, percentage=.1):
        columns = ['name', 'volume', 'avg buy price', 'current price', 'current value', 'net profit',
                   f'{percentage * 100}% value', f'net {percentage * 100}% profit', 'stock exchange', 'arbitrage']

        functions = [self.process_currencies, self.process_cryptocurrencies, self.process_stocks]
        dataframes = [pd.DataFrame(columns=columns) for _ in range(len(functions))]
        threads = [Thread(target=function, args=[percentage, dataframes[i]]) for i, function in enumerate(functions)]

        [t.start() for t in threads]
        [t.join() for t in threads]

        result_df = pd.concat(dataframes)

        result_df.loc['Total'] = pd.Series(result_df[['current value', 'net profit',
                                                      f'{percentage * 100}% value',
                                                      f'net {percentage * 100}% profit']].sum())
        result_df.loc['Total', 'name'] = 'Total'
        result_df.replace('None', '', inplace=True)
        result_df.fillna('', inplace=True)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        return result_df

    def process_stocks(self, percentage, result_df):

        current_price_results = self.data_retriever.get_current_prices_of_stocks(self.shares)
        for current_price_result in current_price_results:
            i = len(result_df)
            current_item = next(item for item in self.shares if item['name'] in current_price_result['name'])
            current_price_result['buy history'] = current_item['buy history']

            self.append_to_dataframe(current_price_result['price'], i, current_price_result['price'], percentage,
                                     result_df, current_price_result)

    def process_cryptocurrencies(self, percentage, result_df):

        for cryptocurrency_asset in self.cryptocurrencies:
            i = len(result_df)
            current_price_result, current_price_percentage = self.data_retriever.get_best_offer_for_cryptocurrency(
                cryptocurrency_asset, DEFAULT_CURRENCY, percentage, DEPTH)

            arbitrage = self.data_retriever.get_arbitrage_for_cryptocurrency(cryptocurrency_asset)

            self.append_to_dataframe(current_price_result[0], i, current_price_percentage[0], percentage, result_df,
                                     cryptocurrency_asset, current_price_result[1].split(':')[0], arbitrage)

    def process_currencies(self, percentage, result_df):

        for currency_asset in self.currencies:
            i = len(result_df)
            current_price_result = self.data_retriever.get_best_offer_for_national_currency(currency_asset,
                                                                                            DEFAULT_CURRENCY)
            self.append_to_dataframe(current_price_result[0], i, current_price_result[0], percentage, result_df,
                                     currency_asset, current_price_result[1].split(':')[0])

    def append_to_dataframe(self, current_price, i, current_price_percentage, percentage, result_df, item,
                            stock_name=None, arbitrage=None):

        if POLISH_STOCK_EXCHAGE_SYMBOL in item['name']:
            current_price = self.convert_zloty_to_default_currency(current_price)

        current_price = self.convert_default_to_base_currency(current_price)
        current_price_percentage = self.convert_default_to_base_currency(current_price_percentage)

        sum_volume = sum(buy['volume'] for buy in item['buy history'])

        average_buy_price = sum(buy['buy price'] * buy['volume'] for buy in item['buy history']) / sum_volume

        result_df.loc[i] = [item['name'], sum_volume, average_buy_price, current_price,
                            current_price * sum_volume,
                            Wallet.calculate_net(item['buy history'], current_price),
                            current_price_percentage * sum_volume * percentage,
                            Wallet.calculate_net(item['buy history'], current_price, percentage), stock_name,
                            str(arbitrage)]

    def add_asset(self, asset):
        if asset['type'] == 'stock':
            asset.pop('type', None)
            existing_item = next((item for item in self.shares if item['name'] in asset['name']), None)
            if not existing_item:
                self.shares.append(asset)
            else:
                existing_item['buy history'] += asset['buy history']
        elif asset['type'] == 'currency':
            asset.pop('type', None)
            existing_item = next((item for item in self.currencies if item['name'] in asset['name']), None)
            if not existing_item:
                self.currencies.append(asset)
            else:
                existing_item['buy history'] += asset['buy history']
        elif asset['type'] == 'cryptocurrency':
            asset.pop('type', None)
            existing_item = next((item for item in self.cryptocurrencies if item['name'] in asset['name']), None)
            if not existing_item:
                self.cryptocurrencies.append(asset)
            else:
                existing_item['buy history'] += asset['buy history']
