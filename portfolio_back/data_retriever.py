import credentials
import quandl

from portfolio_back.api_handler import get_polish_stock_quote
from portfolio_back.finnhub_handler import FinnhubHandler


class DataRetriever:

    def __init__(self, api_key=credentials.FINNHUB_API_KEY):
        self.api_handler = FinnhubHandler(api_key)
        self.forex_markets = self.api_handler.get_forex_markets()
        self.crypto_markets = self.api_handler.get_crypto_markets()
        self.forex_currencies = {}
        for market in self.forex_markets:
            self.forex_currencies[market] = self.api_handler.get_forex_currencies(market.upper())
        self.crypto_currencies = {}
        for market in self.crypto_markets:
            self.crypto_currencies[market] = self.api_handler.get_crypto_currencies(market.upper())

    def get_current_price_summary(self, asset_to_sell):
        return self.api_handler.get_quote(asset_to_sell['name'])

    def get_current_price_of_polish_stock_summary(self, asset_to_sell):
        return get_polish_stock_quote(asset_to_sell['name'])

    def find_best_offer_for_national_currency(self, currency_to_sell, base_currency):
        related_symbols = [currency['symbol'] for market in self.forex_markets for currency
                           in self.forex_currencies[market]
                           if currency_to_sell['name'] in currency['pair'] and base_currency in currency['pair']]

        possible_currency_transactions = []
        for symbol in related_symbols:
            transaction = currency_to_sell.copy()
            transaction['name'] = symbol
            possible_currency_transactions.append(transaction)
        best_offers = [(self.get_current_price_summary(possible_currency_transaction)['c'],
                        possible_currency_transaction['name'].split(':')[0]) for possible_currency_transaction
                       in possible_currency_transactions]
        best_offers = list(filter(None, best_offers))
        return sorted(best_offers, key=lambda o: o[0], reverse=True)[0]

    # def find_best_offer_for_cryptocurrency(self, currency_to_sell, base_currency, percentage=1):
    #     related_symbols = [currency['symbol'] for market in self.crypto_markets for currency
    #                        in self.crypto_currencies[market]
    #                        if currency['pair'] == f"{currency_to_sell['name']}/{base_currency}"]
    #
    #     return self.find_best_offer_for_currency(currency_to_sell, related_symbols, percentage)
