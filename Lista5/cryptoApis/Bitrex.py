from apisUtilities import NORMALIZED_OPERATIONS, get_api_response
from cryptoApis.CryptoApi import CryptoApiInterface
from jsonUtilities import load_data_from_json


def parse_bitrex_orderbook(jsonData):
    resultDictionary = {}
    if jsonData.get("result", None):
        table = []
        if jsonData["result"].get("buy", None):
            pair = []
            for dictionary in jsonData["result"]["buy"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[0]] = table.copy()
            table.clear()
        if jsonData["result"].get("sell", None):
            pair = []
            for dictionary in jsonData["result"]["sell"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[1]] = table.copy()
            table.clear()
    return resultDictionary


def parse_bitrex_currencies(jsonData):
    result = []
    if jsonData.get("result", None):
        for entry in jsonData['result']:
            if entry.get("MarketCurrency", None) and entry.get("BaseCurrency", None):
                result.append((entry['MarketCurrency'], entry['BaseCurrency']))
    return result


class Bitrex(CryptoApiInterface):
    def __init__(self):
        self.__data = load_data_from_json("apis.json")['API']['bitrex']

    def get_offers(self, currency, baseCurrency):
        offers = get_api_response(f'{self.__data["url_orderbook"]}{baseCurrency}'
                                  f'{self.__data["orderbook_separator"]}'
                                  f'{currency}{self.__data["orderbook_ending"]}')
        if offers is not None:
            return parse_bitrex_orderbook(offers)

    def get_taker_fee(self):
        return self.__data['taker_fee']

    def get_markets(self):
        marketInfo = get_api_response(self.__data['url_markets'])
        if marketInfo is not None:
            return parse_bitrex_currencies(marketInfo)

    def get_withdrawal_fees(self):
        fees = get_api_response(self.__data['url_currencies'])
        dictionary = {}
        if fees.get("result", None):
            items = fees['result']
            for entry in items:
                if entry.get('Currency', None) and entry.get('TxFee', None):
                    dictionary[entry['Currency']] = entry["TxFee"]

        return dictionary

    def get_name(self):
        return self.__data['name']
