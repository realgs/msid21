import json
import requests
from arbitrage import get_api_response


def load_api_data_from_json(path="apis.json"):
    try:
        with open(path, 'r') as data:
            result = dict(json.load(data))
            return result
    except json.decoder.JSONDecodeError:
        return dict()

def parse_bitbay_currencies(jsondata):
    result = []
    return result

def parse_bitrex_currencies(jsondata):
    result = []
    return result


def get_currency_pairs(apiinfo, market):
    marketInfo = get_api_response(apiinfo['API'][market]['url_markets'])
    if marketInfo is not None:
        if market == apiinfo['Api']['bitbay']['name']:
            return parse_bitbay_currencies(marketInfo)
        elif market == apiinfo['Api']['birex']['name']:
            return parse_bitrex_currencies(marketInfo)


def find_common_currencies_pairs():
    apiInfo = load_api_data_from_json()
    bitbayPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitbay']['name'])
    bitrexPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitrex']['name'])


if __name__ == '__main__':
    print('PyCharm')
