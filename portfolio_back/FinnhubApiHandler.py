import json

import finnhub
import websocket


class FinnhubApiHandler:

    def __init__(self, api_key):
        self.api_key = api_key
        self.finnhub_client = finnhub.Client(api_key=self.api_key)

    def get_forex_markets(self):
        return self.finnhub_client.forex_exchanges()

    def get_forex_currencies(self, market):
        return [currency['displaySymbol'] for currency in self.finnhub_client.forex_symbols(market)]

    def get_forex_rates(self, currency):
        return self.finnhub_client.forex_rates(base=currency)

    def get_crypto_markets(self):
        return self.finnhub_client.crypto_exchanges()

    def get_crypto_currencies(self, market):
        return [{'pair': currency['displaySymbol'], 'symbol': currency['symbol']} for currency in
                self.finnhub_client.crypto_symbols(market)]

    def get_last_orders(self, item, market=''):
        market += ':' if market != '' else market
        ws = websocket.create_connection(f"wss://ws.finnhub.io?token={self.api_key}")
        query = {'type': 'subscribe', 'symbol': market + item}
        ws.send(json.dumps(query))
        result = ws.recv()
        ws.close()
        return result
