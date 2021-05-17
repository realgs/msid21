import json

import pandas as pd

from portfolio_back.data_retriever import DataRetriever

TAX_RATIO = .19


class Asset:

    def __init__(self, price, volume, name, base_currency):
        self.price = price
        self.volume = volume
        self.name = name
        self.base_currency = base_currency

    def __repr__(self):
        return f"{self.volume} {self.name} for price: {self.price}{self.base_currency}"


class Wallet:

    def __init__(self, wallet_path):
        temp_wallet = Wallet.read_wallet(wallet_path)
        self.base_currency = temp_wallet['base currency']
        self.currencies = temp_wallet['assets']['currencies']
        self.cryptocurrencies = temp_wallet['assets']['cryptocurrencies']
        self.foreign_shares = temp_wallet['assets']['foreign_shares']
        self.polish_shares = temp_wallet['assets']['polish_shares']
        self.data_retriever = DataRetriever()

    @staticmethod
    def read_wallet(wallet_path):
        with open(wallet_path, 'r') as f:
            temp_wallet = json.load(f)
        return temp_wallet

    @staticmethod
    def calculate_net(volume, buy_price, sell_price, tax=TAX_RATIO):
        gross = volume * sell_price - volume * buy_price
        return gross if gross <= 0 else (1 - tax) * gross

    def get_complete_assets_dataframe(self, percentage=.1):
        columns = ['name', 'volume', 'buy price', 'current price', 'current value', 'net value',
                   f'{percentage * 100}% value', f'net {percentage * 100}% value', 'stock exchange', 'arbitrage']
        result_df = pd.DataFrame(columns=columns)

        # for i, currency_asset in enumerate(self.currencies):
        #     current_value = self.data_retriever.find_best_offer_for_national_currency(currency_asset,
        #                                                                                           self.base_currency)
        #     current_value_percentage = self.data_retriever.find_best_offer_for_national_currency(currency_asset,
        #                                                                                          self.base_currency,
        #                                                                                          percentage)
        #     result_df.loc[i] = [currency_asset['name'], currency_asset['volume'], currency_asset['buy price'],
        #                         current_value['p'], Wallet.calculate_net(currency_asset['volume'],
        #                                                                  currency_asset['buy price'],
        #                                                                  current_value['p']),
        #                         current_value_percentage, Wallet.calculate_net(currency_asset['volume'] * percentage,
        #                                                                        currency_asset['buy price'],
        #                                                                        current_value_percentage['p']),
        #                         current_value['s'].split(':')[0], None]

        for currency_asset in self.currencies:
            i = len(result_df)
            current_value = self.data_retriever.find_best_offer_for_national_currency(currency_asset,
                                                                                      self.base_currency)
            result_df.loc[i] = [currency_asset['name'], currency_asset['volume'],
                                currency_asset['buy price'], current_value[0],
                                current_value[0] * currency_asset['volume'],
                                Wallet.calculate_net(currency_asset['volume'], currency_asset['buy price'],
                                                     current_value[0]),
                                current_value[0] * currency_asset['volume'] * percentage,
                                Wallet.calculate_net(currency_asset['volume'] * percentage, currency_asset['buy price'],
                                                     current_value[0]),
                                current_value[1].split(':')[0], None]

        for share in self.polish_shares:
            i = len(result_df)
            current_value = self.data_retriever.get_current_price_of_polish_stock_summary(share)['close']
            result_df.loc[i] = [share['name'], share['volume'], share['buy price'], current_value,
                                current_value * share['volume'],
                                Wallet.calculate_net(share['volume'], share['buy price'], current_value),
                                current_value * share['volume'] * percentage,
                                Wallet.calculate_net(share['volume'] * percentage, share['buy price'],
                                                     current_value), None, None]

        for share in self.foreign_shares:
            i = len(result_df)
            current_value = self.data_retriever.get_current_price_summary(share)['c']
            result_df.loc[i] = [share['name'], share['volume'], share['buy price'], current_value,
                                current_value * share['volume'],
                                Wallet.calculate_net(share['volume'], share['buy price'], current_value),
                                current_value * share['volume'] * percentage,
                                Wallet.calculate_net(share['volume'] * percentage, share['buy price'],
                                                     current_value), None, None]

        pd.set_option("display.max_rows", None, "display.max_columns", None)
        return result_df


if __name__ == '__main__':
    wallet = Wallet(r'D:\Studia\IV semestr\MSiD\Lab\Lista5\wallet.json')
    print(wallet.get_complete_assets_dataframe())
