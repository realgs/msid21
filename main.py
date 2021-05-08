import requests
import CommonCurrencies

BITBAY_MARKETS = "https://api.bitbay.net/rest/trading/ticker"
BITBAY_ORDERBOOK = "https://bitbay.net/API/Public/"
BITBAY_ORDER = '/orderbook.json'
BITBAY_TAKER_FEE = 0.0043

BITTREX_MARKETS = "https://api.bittrex.com/v3/markets/"
BITTREX_ORDER = '/orderbook'
BITTREX_ORDERBOOK = "https://api.bittrex.com/v3/markets/"
BITTREX_TAKER_FEE = 0.0025

CONNECTION_FAILED = "Connection failed"
markets = ['bitbay', 'bittrex']


def connect_with_api(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print(CONNECTION_FAILED)
        return None


def get_bitbay_data(bitbay_json):
    result = []

    bitbay_items = bitbay_json['items']
    bitbay_keys = bitbay_items.keys()

    for element in bitbay_keys:
        result.append(element)

    return result


def get_bittrex_data(bittrex_json):
    result = []

    for element in range(0, len(bittrex_json)):
        result.append(bittrex_json[element]['symbol'])

    return result


if __name__ == '__main__':
    response_bitbay = get_bitbay_data(connect_with_api(BITBAY_MARKETS))
    response_bittrex = get_bittrex_data(connect_with_api(BITTREX_MARKETS))

    # exercise 1
    print("Common currencies for bitbay and bittrex: ")
    print(CommonCurrencies.get_common_markets(response_bitbay, response_bittrex))
