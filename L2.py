import requests
import time
import json
from threading import Thread

OFFERS_TO_PRINT = 4


def get_data(url):
    response = requests.get(url)
    data = json.loads(response.content)
    if response.status_code == 200:
        return data
    else:
        return None


def show_currency_offers(cryptocurrency, snd_currency):
    data = get_data(f"https://bitbay.net/API/Public/{cryptocurrency}{snd_currency}/orderbook.json")
    if data is not None:
        print(f"\n{cryptocurrency}/{snd_currency}")
        print("Bids: ")
        bids = data["bids"]
        for i in range(OFFERS_TO_PRINT):
            print(bids[i])
        print("\n Asks: ")
        asks = data["asks"]
        for i in range(OFFERS_TO_PRINT):
            print(asks[i])
    else:
        print("Failed to get currency data")


def show_currency_data(cryptocurrency, snd_currency):
    while True:
        data = get_data(f"https://bitbay.net/API/Public/{cryptocurrency}{snd_currency}/orderbook.json")
        if data is not None:
            bids = data["bids"]
            asks = data["asks"]
            difference = (1 - (float(asks[0][0]) - float(bids[0][0])) / float(bids[0][0])) * 100
            print(f"{cryptocurrency}/{snd_currency} buy/sell difference: {round(difference, 3)}%")
        else:
            print("Failed to get currency data")
        time.sleep(5)


def ex1():
    show_currency_offers("BTC", "USD")
    time.sleep(0.3)
    show_currency_offers("LTC", "USD")
    time.sleep(0.3)
    show_currency_offers("DASH", "USD")
    time.sleep(0.3)


def ex2():
    bg_thread = Thread(target=show_currency_data, args=("BTC", "USD"), daemon=True)
    bg_thread.start()
    input("\nPress enter to exit\n")


def main():
    ex1()
    ex2()


if __name__ == "__main__":
    main()
