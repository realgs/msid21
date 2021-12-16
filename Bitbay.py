import requests
import market
import constants_bitbay
import constants


class Bitbay(market.Market):
    def __init__(self, taker_fee):
        super().__init__('Bitbay', taker_fee)
        self.pairs = self.get_pairs()

    def get_orderbook(self, pair, limit):
        result = {constants.STATUS: constants_bitbay.OK, constants.BIDS: [], constants.ASKS: []}
        response = requests.get(constants_bitbay.URL + constants_bitbay.ORDERBOOK + pair + '/' + str(limit))
        if response.status_code == constants.OK_RESPONSE:
            response = response.json()
            if not response[constants_bitbay.STATUS] == constants_bitbay.STATUS_FAIL:
                for bid in response[constants_bitbay.BUY_KEY]:
                    result[constants.BIDS].append(
                        [float(bid[constants_bitbay.RATE_KEY]), float(bid[constants_bitbay.QUANTITY_KEY])])
                result[constants.BIDS].reverse()  # bids from bitbay rest in the wrong order
                for ask in response[constants_bitbay.SELL_KEY]:
                    result[constants.ASKS].append(
                        [float(ask[constants_bitbay.RATE_KEY]), float(ask[constants_bitbay.QUANTITY_KEY])])
            else:
                result[constants.STATUS] = constants_bitbay.ERROR_MARKET_NOT_RECOGNIZED
        else:
            result[constants.STATUS] = response.status_code
        return result

    def get_pairs(self):
        pairs = {constants.STATUS: constants_bitbay.OK}
        response = requests.get(constants_bitbay.URL + constants_bitbay.STATS)
        if response.status_code == constants.OK_RESPONSE:
            response = response.json()
            for i in response[constants_bitbay.ITEMS_KEY]:
                splitted = i.split(constants_bitbay.PAIR_SEPARATOR)
                pairs[(splitted[0], splitted[1])] = i
        else:
            pairs[constants.STATUS] = response.status_code
        return pairs
