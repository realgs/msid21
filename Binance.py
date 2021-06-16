import market
import requests
import constants_binance
import constants

class Binance(market.Market):
    def __init__(self, taker_fee):
        super().__init__('Binance', taker_fee)
        self.pairs = self.get_pairs()

    def get_orderbook(self, pair, limit):
        params = {
            'symbol': pair,
            'limit': limit
        }
        response = requests.request("GET", constants_binance.URL + constants_binance.ORDERBOOK, params=params)
        result = {constants.STATUS: constants_binance.OK, constants.BIDS: [], constants.ASKS: []}
        if response.status_code == constants.OK_RESPONSE:
            r = response.json()
            del r['lastUpdateId']

            for i in r[constants.ASKS]:
                result[constants.ASKS].append([float(i[0]), float(i[1])])
            for i in r[constants.BIDS]:
                result[constants.BIDS].append([float(i[0]), float(i[1])])
        else:
            result[constants.STATUS] = response.status_code
        return result

    def get_pairs(self):
        pairs = {constants.STATUS: constants_binance.OK}
        response = requests.get(constants_binance.URL + constants_binance.EXCHANGE_INFO)
        if response.status_code == constants.OK_RESPONSE:
            response = response.json()
            for i in response[constants_binance.SYMBOLS_KEY]:
                pairs[(i[constants_binance.BASE_ASSET], i[constants_binance.QUOTE_ASSET])] = i[constants_binance.BASE_ASSET] + i[constants_binance.QUOTE_ASSET]
        else:
            pairs[constants.STATUS] = response.status_code
        return pairs
