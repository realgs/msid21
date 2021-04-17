from math import fabs
import requests

BTC = 'BTC'
# BSV = 'BSV'
BASE_CURRENCY = 'USD'
BITBAY_URL = "https://bitbay.net/API/Public/{}/orderbook.json".format(BTC + BASE_CURRENCY)
BITTREX_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(BASE_CURRENCY, BTC)
DELAY = 5
ROUND = 3
markets = ['bitbay.net', 'bittrex.com']


def connect_with_api(api):
    try:
        response = requests.get(api)
        if response.status_code in range(200, 299):
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print("Connection failed")
        return None


def get_bitbay_data(response):
    bids_bitbay = response['bids'][0][0]
    asks_bitbay = response['asks'][0][0]

    return bids_bitbay, asks_bitbay


def get_bittrex_data(response):
    bids_bittrex = response['result']['buy'][0]['Rate']
    asks_bittrex = response['result']['sell'][0]['Rate']

    return bids_bittrex, asks_bittrex


def calculate_percentage_difference(price1, price2):
    return round((1 - (price1 - price2)) / price2 * 100, ROUND)


def print_differences(bitbay_data, bittrex_data):
    bitbay = get_bitbay_data(bitbay_data)
    bittrex = get_bittrex_data(bittrex_data)

    print(f"Buying price difference: {calculate_percentage_difference(bitbay[0], bittrex[0])}%")
    print(f"Selling price difference: {calculate_percentage_difference(bitbay[1], bittrex[1])}%")
    print(f"Buying price in {markets[0]} to selling price in {markets[1]}: {calculate_percentage_difference(bitbay[1], bittrex[0])}%")
    print(f"Buying price in {markets[1]} to selling price in {markets[0]}: {calculate_percentage_difference(bittrex[1], bitbay[0])}%")


if __name__ == '__main__':
    response_bitbay = connect_with_api(BITBAY_URL)
    response_bittrex = connect_with_api(BITTREX_URL)

    if response_bitbay and response_bittrex:
        print_differences(response_bitbay, response_bittrex)
