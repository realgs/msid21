import constants_binance
import constants
import requests
import market
import datetime


def req_api(point):
    result = None
    response = requests.get(constants_binance.URL + point)
    if response.status_code == constants.STATUS_OK:
        result = response.json()
    else:
        result = response.status_code
    return result


def get_pairs():
    pairs = set()
    response = req_api(constants_binance.EXCHANGE_INFO)
    for i in response[constants_binance.SYMBOLS_KEY]:
        pairs.add(frozenset([i[constants_binance.BASE_ASSET], i[constants_binance.QUOTE_ASSET]]))
    return pairs


def get_orderbook(pair, limit):
    result = None

    params = {
        constants_binance.SYMBOL_PARAM : pair,
        constants_binance.LIMIT_PARAM : limit
    }

    response = requests.request("GET", constants_binance.URL+constants_binance.ORDERBOOK, params=params)
    if response.status_code == constants.STATUS_OK:
        r = response.json()
        del r[constants_binance.LAST_UPDATE_ID]

        result = {constants.BIDS: [], constants.ASKS: []}

        for i in r[constants.ASKS]:
            result[constants.ASKS].append([float(i[0]), float(i[1])])
        for i in r[constants.BIDS]:
            result[constants.BIDS].append([float(i[0]), float(i[1])])
    else:
        result = response.status_code
    return result


def create_market():
    return market.Market(constants_binance.NAME, get_pairs())
