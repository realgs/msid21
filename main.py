import requests

import time


API_URL = "https://bitbay.net/API/Public/"
CURRENCIES = ["BTC", "LTC", "DASH"]
BASE_CURRENCY = "USD"
SINGLE_OFFER = 1
DEF_NO_OF_OFFERS = 5
SLEEP_TIME = 5


def get_response(url):
    api_response = requests.get(url)
    if api_response.status_code == 200:
        return api_response.json()
    else:
        print("Could not connect to API.", api_response.reason)
        return None


def get_offers(crypto_currency, no_of_offers):
    all_offers = get_response(API_URL + crypto_currency + BASE_CURRENCY + "/orderbook.json")
    if all_offers is None:
        return None
    else:
        return {'bids': (all_offers['bids'][:no_of_offers]), 'asks': (all_offers['asks'][:no_of_offers])}


def print_offers(crypto_currency):
    all_offers = get_offers(crypto_currency, DEF_NO_OF_OFFERS)
    if all_offers is None:
        print("Could not connect to API.")
    else:
        bids = all_offers['bids']
        asks = all_offers['asks']
        print(crypto_currency, "buy offers:")
        for bid in bids:
            print(f'\t{bid[1]} {crypto_currency} for {bid[0] * bid[1]:.2f} {BASE_CURRENCY} '
                  f'/// Exchange rate: {bid[0]:.2f} {BASE_CURRENCY} for 1 {crypto_currency}')
        print(crypto_currency, "sell offers:")
        for ask in asks:
            print(f'\t{ask[1]} {crypto_currency} for {ask[0] * ask[1]:.2f} {BASE_CURRENCY} '
                  f'/// Exchange rate: {ask[0]:.2f} {BASE_CURRENCY} for 1 {crypto_currency}')


def calculate_profit(crypto_currency):
    while True:
        all_offers = get_offers(crypto_currency, SINGLE_OFFER)
        if all_offers is None:
            print("Could not connect to API.")
        else:
            bids = all_offers['bids']
            asks = all_offers['asks']
            buy_to_sell_ratio = (1 + bids[0][0] - asks[0][0]) / bids[0][0]
            print(f'Profits for {crypto_currency}: {buy_to_sell_ratio * 100:.2f}%')
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    print("----EXERCISE 1:")
    print_offers(CURRENCIES[0])
    print_offers(CURRENCIES[1])
    print_offers(CURRENCIES[2])
    print()

    print("----EXERCISE 2:")
    calculate_profit(CURRENCIES[0])  # endless loop - refresh every 5 sec
    # calculate_profit(CURRENCIES[1])  # endless loop - refresh every 5 sec
    # calculate_profit(CURRENCIES[2])  # endless loop - refresh every 5 sec

