import json
import requests


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def load_api_data_from_json(path="apis.json"):
    try:
        with open(path, 'r') as data:
            result = dict(json.load(data))
            return result
    except json.decoder.JSONDecodeError:
        return dict()


def get_bitrex_fees(apiinfo):
    fees = get_api_response(apiinfo['API']['bitrex']['url_currencies'])
    dictionary = {}
    if fees.get("result", None):
        items = fees['result']
        for entry in items:
            if entry.get('Currency', None) and entry.get('TxFee', None):
                dictionary[entry['Currency']] = entry["TxFee"]

    return dictionary


def get_transfer_fees(apiinfo, pairs):
    fees = {"bitbay": {}, "bitrex": {}}
    bitrexFees = get_bitrex_fees(apiinfo)
    for pair in pairs:
        fees['bitbay'][pair[0]] = apiinfo['FEES']["bitbay_fees"][pair[0]]
        fees['bitrex'][pair[0]] = bitrexFees[pair[0]]
    return fees

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


def find_common_currencies_pairs(apiinfo):
    bitbayPairs = get_currency_pairs(apiinfo, apiinfo['API']['bitbay']['name'])
    bitrexPairs = get_currency_pairs(apiinfo, apiinfo['API']['bitrex']['name'])

    return set(bitrexPairs).intersection(bitbayPairs)
