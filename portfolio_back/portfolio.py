import json

import pandas as pd

from portfolio_back.data_retriever import DataRetriever

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
        return amount / self.zloty_to_default_currency

    @staticmethod
    def calculate_net(volume, buy_price, sell_price, tax=TAX_RATIO):
        gross = volume * sell_price - volume * buy_price
        return gross if gross <= 0 else (1 - tax) * gross

    def get_complete_assets_dataframe(self, percentage=.1):
        columns = ['name', 'volume', 'buy price', 'current price', 'current value', 'net profit',
                   f'{percentage * 100}% value', f'net {percentage * 100}% profit', 'stock exchange', 'arbitrage']
        result_df = pd.DataFrame(columns=columns)

        for currency_asset in self.currencies:
            i = len(result_df)
            current_price_result = self.data_retriever.get_best_offer_for_national_currency(currency_asset,
                                                                                            DEFAULT_CURRENCY)
            self.append_to_dataframe(current_price_result[0], i, current_price_result[0], percentage, result_df,
                                     currency_asset, current_price_result[1].split(':')[0])

        for cryptocurrency_asset in self.cryptocurrencies:
            i = len(result_df)
            current_price_result, current_price_percentage = self.data_retriever.get_best_offer_for_cryptocurrency(
                cryptocurrency_asset, DEFAULT_CURRENCY, percentage, DEPTH)

            arbitrage = self.data_retriever.get_arbitrage_for_cryptocurrency(cryptocurrency_asset)
            arbitrage.profit = arbitrage.profit * cryptocurrency_asset['volume'] / arbitrage.quantity

            self.append_to_dataframe(current_price_result[0], i, current_price_percentage[0], percentage, result_df,
                                     cryptocurrency_asset, current_price_result[1].split(':')[0], arbitrage)

        current_price_results = self.data_retriever.get_current_prices_of_stocks(self.shares)
        for current_price_result in current_price_results:
            i = len(result_df)
            current_item = next(item for item in self.shares if item['name'] in current_price_result['name'])
            current_price_result['volume'], current_price_result['buy price'] = \
                current_item['volume'], current_item['buy price']

            self.append_to_dataframe(current_price_result['price'], i, current_price_result['price'], percentage,
                                     result_df, current_price_result)

        result_df.loc['Total'] = pd.Series(result_df[['current value', 'net profit',
                                                      f'{percentage * 100}% value',
                                                      f'net {percentage * 100}% profit']].sum())
        result_df.loc['Total', 'name'] = 'Total'
        result_df.fillna('', inplace=True)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        return result_df

    def append_to_dataframe(self, current_price, i, current_price_percentage, percentage, result_df, item,
                            stock_name=None, arbitrage=None):

        current_price = self.convert_default_to_base_currency(current_price)
        current_price_percentage = self.convert_default_to_base_currency(current_price_percentage)

        result_df.loc[i] = [item['name'], item['volume'], item['buy price'], current_price,
                            current_price * item['volume'],
                            Wallet.calculate_net(item['volume'], item['buy price'], current_price),
                            current_price_percentage * item['volume'] * percentage,
                            Wallet.calculate_net(item['volume'] * percentage, item['buy price'],
                                                 current_price), stock_name, arbitrage]

    def add_asset(self, asset):
        if asset['type'] == 'stock':
            asset.pop('type', None)
            asset['buy price'] = asset.pop('price')
            self.shares.append(asset)
        elif asset['type'] == 'currency':
            asset.pop('type', None)
            asset['buy price'] = asset.pop('price')
            self.currencies.append(asset)
        elif asset['type'] == 'cryptocurrency':
            asset.pop('type', None)
            asset['buy price'] = asset.pop('price')
            self.cryptocurrencies.append(asset)
