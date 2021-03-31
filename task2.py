import time
import requests

BIDS = 'bids'
ASKS = 'asks'
ADDRESS_BITBAY = 'https://bitbay.net/API/Public/'
ADDRESS_ORDERBOOK = '/orderbook.json'
BASE_CURRENCY = 'USD'


def get_data(currencies):
    address = ADDRESS_BITBAY + currencies + ADDRESS_ORDERBOOK
    return requests.get(address)


def print_difference(currencies, bid, ask, diff):
    print(currencies, "sell:", ask, ", purchase:", bid)
    print(currencies, "Difference:", diff, "%")


def print_bids_asks_difference(crypto_currency):
    currencies = crypto_currency + BASE_CURRENCY
    response = get_data(currencies)
    if response:
        response_json = response.json()

        bid = response_json[BIDS][0][0]
        ask = response_json[ASKS][0][0]
        diff = (1 - (ask - bid) / bid) * 100
        print_difference(currencies, bid, ask, diff)
    else:
        print(currencies, ' data not found')


def print_updating_data(currencies, delay):
    while True:
        print_bids_asks_difference(currencies)
        time.sleep(delay)


def main():
    print_bids_asks_difference('BTC')
    print_bids_asks_difference('DASH')
    print_bids_asks_difference('LTC')
    print_updating_data('BTC', 5)


if __name__ == '__main__':
    main()

