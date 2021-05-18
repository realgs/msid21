import finnhub
import requests


class FinnhubHandler:

    def __init__(self, api_key):
        self.api_key = api_key
        try:
            self.finnhub_client = finnhub.Client(api_key=self.api_key)
        except requests.exceptions.SSLError:
            print("ERROR. Connection with Finnhub not established")

    def get_forex_markets(self):
        return self.finnhub_client.forex_exchanges()

    def get_forex_currencies(self, market):
        return [{'pair': currency['displaySymbol'], 'symbol': currency['symbol']} for currency in
                self.finnhub_client.forex_symbols(market)]

    def get_forex_rates(self, currency):
        return self.finnhub_client.forex_rates(base=currency)

    def get_crypto_markets(self):
        return self.finnhub_client.crypto_exchanges()

    def get_crypto_currencies(self, market):
        return [{'pair': currency['displaySymbol'], 'symbol': currency['symbol']} for currency in
                self.finnhub_client.crypto_symbols(market)]

    def get_quote(self, asset_name):
        try:
            return self.finnhub_client.quote(asset_name)
        except requests.exceptions.ReadTimeout:
            print("TIMEOUT ERROR. Try again later")

        return None
