import constants_bitbay
import constants
import requests
import market


def req_api(point):
    result = None
    response = requests.get(constants_bitbay.URL + point)
    if response.status_code == constants.STATUS_OK:
        result = response.json()
    else:
        result = response.status_code
    return result


def get_pairs():
    pairs = set()
    response = req_api(constants_bitbay.STATS)
    for i in response[constants_bitbay.ITEMS_KEY]:
        splitted = i.split(constants_bitbay.PAIR_SEPARATOR)
        pairs.add(frozenset([splitted[0], splitted[1]]))
    return pairs


def get_orderbook(pair, limit):
    result = {constants.BIDS: [], constants.ASKS: []}
    r = req_api(constants_bitbay.ORDERBOOK_LIM+pair+"/"+str(limit))
    del r[constants_bitbay.STATUS_KEY]
    for bid in r[constants_bitbay.BUY_KEY]:
        result[constants.BIDS].append([float(bid[constants_bitbay.RATE_KEY]), float(bid[constants_bitbay.QUANTITY_KEY])])
    for ask in r[constants_bitbay.SELL_KEY]:
        result[constants.ASKS].append([float(ask[constants_bitbay.RATE_KEY]), float(ask[constants_bitbay.QUANTITY_KEY])])
    return result

def create_market():
    return market.Market(constants_bitbay.NAME, get_pairs())
