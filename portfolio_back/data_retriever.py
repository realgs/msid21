import json

import credentials
from portfolio_back.arbitrages import get_arbitrage
from portfolio_back.offers import get_bidlist

from portfolio_back.utils import get_stocks_quotes, get_current_exchange_rate
from portfolio_back.finnhub_handler import FinnhubHandler

DEFAULT_DEPTH = 50


class DataRetriever:

    def __init__(self, api_key=credentials.FINNHUB_API_KEY):
        self.api_handler = FinnhubHandler(api_key)
        self.forex_markets, self.crypto_markets, self.forex_currencies, self.crypto_currencies = \
            DataRetriever.read_default_config()

    def save_default_config(self, output_file='data_retriever_config.json'):
        config_dict = {
            'forex markets': self.forex_markets,
            'forex currencies': self.forex_currencies,
            'crypto markets': self.crypto_markets,
            'crypto currencies': self.crypto_currencies
        }

        with open(output_file, 'w') as f:
            json.dump(config_dict, f)

    @staticmethod
    def read_default_config(input_file='portfolio_back/data_retriever_config.json'):
        with open(input_file, 'r') as f:
            config_dict = json.load(f)

        return config_dict['forex markets'], config_dict['crypto markets'], config_dict['forex currencies'], \
               config_dict['crypto currencies']

    def get_current_price_summary(self, asset_to_sell):
        return self.api_handler.get_quote(asset_to_sell['name'])

    def get_current_prices_of_stocks(self, assets_to_sell):
        returned_json = get_stocks_quotes([asset_to_sell['name'] for asset_to_sell in assets_to_sell])
        return [{'name': item['code'], 'price': item['close']} for item in returned_json]

    def get_exchange_rate(self, currency_to_sell_symbol, base_currency_symbol):
        return float(get_current_exchange_rate(currency_to_sell_symbol, base_currency_symbol)[
                         'Realtime Currency Exchange Rate']['5. Exchange Rate'])

    def get_best_offer_for_national_currency(self, currency_to_sell, base_currency):
        related_symbols = [currency['symbol'] for market in self.forex_markets for currency
                           in self.forex_currencies[market]
                           if currency_to_sell['name'] in currency['pair'] and base_currency in currency['pair']]

        best_offer = self.find_best_finnhub_price_for_currency(currency_to_sell, related_symbols)
        best_offer_pair_name = next((currency['pair'] for market in self.forex_markets for currency
                                     in self.forex_currencies[market]
                                     if best_offer[2] in currency['symbol']), None)

        best_offer_price = 1 / best_offer[
            0] if best_offer_pair_name != f"{currency_to_sell['name']}/{base_currency}" else best_offer[0]

        return best_offer_price, best_offer[1]

    def get_best_offer_for_cryptocurrency(self, currency_to_sell, base_currency, percentage=1, num_offers=50):
        related_symbols = [currency['symbol'] for market in self.crypto_markets for currency
                           in self.crypto_currencies[market]
                           if currency['pair'] == f"{currency_to_sell['name']}/{base_currency}"]

        finnhub_result = self.find_best_finnhub_price_for_currency(currency_to_sell, related_symbols)
        orderbooks_result = self.check_orderbooks(currency_to_sell, base_currency, DEFAULT_DEPTH, 1)
        orderbooks_result_percentage = self.check_orderbooks(currency_to_sell, base_currency, num_offers, percentage)

        return finnhub_result if finnhub_result[0] > orderbooks_result[0] else orderbooks_result, \
               orderbooks_result_percentage

    def get_arbitrage_for_cryptocurrency(self, currency):
        return get_arbitrage(currency['name'])

    def find_best_finnhub_price_for_currency(self, currency_to_sell, related_symbols):
        possible_currency_transactions = []
        for symbol in related_symbols:
            transaction = currency_to_sell.copy()
            transaction['name'] = symbol
            possible_currency_transactions.append(transaction)
        best_offers = [(self.get_current_price_summary(possible_currency_transaction)['c'],
                        possible_currency_transaction['name'].split(':')[0],
                        possible_currency_transaction['name'].split(':')[1]) for possible_currency_transaction
                       in possible_currency_transactions]
        best_offers = list(filter(None, best_offers))
        return sorted(best_offers, key=lambda o: o[0], reverse=True)[0]

    def check_orderbooks(self, currency_to_sell, base_currency, num_offers, percentage):
        bid_dict = get_bidlist(currency_to_sell['name'] + '-' + base_currency, num_offers)
        sum_volume = sum(buy['volume'] for buy in currency_to_sell['buy history'])
        volume = sum_volume * percentage
        best_offer = -1
        best_site = ''
        for site in bid_dict.keys():
            for bid in bid_dict[site]:
                if bid.quantity >= volume and bid.price > best_offer:
                    best_offer = bid.price
                    best_site = site

        return best_offer, best_site
