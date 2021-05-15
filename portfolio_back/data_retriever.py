import credentials
from portfolio_back.finnhub_api_handler import FinnhubApiHandler


class DataRetriever:

    def __init__(self, api_key=credentials.API_KEY):
        self.api_handler = FinnhubApiHandler(api_key)
        self.forex_markets = self.api_handler.get_forex_markets()
        self.crypto_markets = self.api_handler.get_crypto_markets()
        self.forex_currencies = {}
        for market in self.forex_markets:
            self.forex_currencies[market] = self.api_handler.get_forex_currencies(market.upper())
        self.crypto_currencies = {}
        for market in self.crypto_markets:
            self.crypto_currencies[market] = self.api_handler.get_crypto_currencies(market.upper())

    def find_best_offer(self, symbol, asset_to_sell, market='', min_depth=50):
        offers = self.api_handler.get_last_orders(symbol, market)
        while len(offers) < min_depth:
            offers + self.api_handler.get_last_orders(symbol, market)

        fitting_offers = []
        for offer in offers:
            if offer['v'] >= asset_to_sell.volume:
                fitting_offers.append(offer)

        if not fitting_offers:
            fitting_offers = offers

        return sorted(fitting_offers, key=lambda o: o['v'], reverse=True)[0]
