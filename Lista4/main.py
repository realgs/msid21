import requests
from common import get_api_response, load_api_data_from_json


def parse_bitbay_currencies(jsondata):
    result = []
    if jsondata.get("items", None):
        items = jsondata['items']
        for entry in items.keys():
            pair = entry.split('-')
            result.append((pair[0], pair[1]))
    return result


def parse_bitrex_currencies(jsondata):
    result = []
    if jsondata.get("result", None):
        for entry in jsondata['result']:
            if entry.get("MarketCurrency", None) and entry.get("BaseCurrency", None):
                result.append((entry['MarketCurrency'], entry['BaseCurrency']))
    return result


def get_currency_pairs(apiinfo, market):
    marketInfo = get_api_response(apiinfo['API'][market]['url_markets'])
    if marketInfo is not None:
        if market == apiinfo['API']['bitbay']['name']:
            return parse_bitbay_currencies(marketInfo)
        elif market == apiinfo['API']['bitrex']['name']:
            return parse_bitrex_currencies(marketInfo)


def find_common_currencies_pairs():
    apiInfo = load_api_data_from_json()
    bitbayPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitbay']['name'])
    bitrexPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitrex']['name'])

    return set(bitrexPairs).intersection(bitbayPairs)


if __name__ == '__main__':
    try:
        pairs = find_common_currencies_pairs()
        for x in pairs:
            print(x)
    except requests.ConnectionError:
        print("Failed to connect to API")
