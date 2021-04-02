import requests
import time
import json
import random
from threading import Thread

DEFAULT_OFFERS_COUNT = 4
API_URL = "https://bitbay.net/API/Public/{0}{1}/{2}"
REQUEST_TYPE_ORDERBOOK = "orderbook.json"
BASE_CURRENCY = "USD"
CRYPTOCURRENCIES = ["BTC", "LTC", "DASH", "XRP", "BCC"]


def get_data_from_url(url):
    response = requests.get(url)
    if 200 <= response.status_code <= 299:
        data = json.loads(response.content)
        return data
    else:
        return None


def show_currency_offers(cryptocurrency, snd_currency, offers_count=DEFAULT_OFFERS_COUNT):
    data = get_data_from_url(API_URL.format(cryptocurrency, snd_currency, REQUEST_TYPE_ORDERBOOK))
    if data is not None:
        print(f"\n{cryptocurrency}/{snd_currency}")
        print("Bids: ")
        bids = data["bids"]
        display_range = offers_count
        if len(bids) < offers_count:
            display_range = len(bids)
        for i in range(display_range):
            print(bids[i])

        print("\n Asks: ")
        asks = data["asks"]
        if len(asks) < display_range:
            display_range = len(asks)
        for i in range(display_range):
            print(asks[i])
    else:
        print("Failed to get currency data")


def show_currency_data(cryptocurrency, snd_currency):
    while True:
        data = get_data_from_url(API_URL.format(cryptocurrency, snd_currency, REQUEST_TYPE_ORDERBOOK))
        if data is not None:
            bids = data["bids"]
            asks = data["asks"]
            difference = (1 - (float(asks[0][0]) - float(bids[0][0])) / float(bids[0][0])) * 100
            print(f"{cryptocurrency}/{snd_currency} buy/sell difference: {round(difference, 3)}%")
        else:
            print("Failed to get currency data")
        time.sleep(5)


def ex1():
    for crypto in CRYPTOCURRENCIES:
        show_currency_offers(crypto, BASE_CURRENCY, random.randint(2, 6))
        time.sleep(0.05)


def ex2():
    bg_thread = Thread(target=show_currency_data, args=("BTC", BASE_CURRENCY), daemon=True)
    bg_thread.start()
    input("\nType exit and press enter to exit program\n")


def main():
    ex1()
    ex2()


if __name__ == "__main__":
    main()
