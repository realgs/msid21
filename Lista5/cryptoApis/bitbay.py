from jsonUtilities import load_data_from_json
from apisUtilities import get_api_response


def parse_bitbay_currencies(jsonData):
    result = []
    if jsonData.get("items", None):
        items = jsonData['items']
        for entry in items.keys():
            pair = entry.split('-')
            result.append((pair[0], pair[1]))
    return result


class Bitbay:
    def __init__(self):
        self.__data = load_data_from_json("apis.json")['API']['bitbay']
        self.__fees = load_data_from_json("apis.json")['FEES']["bitbay_fees"]

    def get_offers(self, currency, baseCurrency):
        offers = get_api_response(f'{self.__data["url_orderbook"]}{currency}'
                                  f'{baseCurrency}{self.__data["orderbook_ending"]}')
        if offers is not None:
            return offers

    def get_taker_fee(self):
        return self.__data['taker_fee']

    def get_markets(self):
        marketInfo = get_api_response(self.__data['url_markets'])
        if marketInfo is not None:
            return parse_bitbay_currencies(marketInfo)

    def get_withdrawal_fees(self):
        return self.__fees

    def get_name(self):
        return self.__data['name']
