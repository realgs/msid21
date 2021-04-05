import threading
import time
import requests

SLEEP = 5
REPLIES = 3
BASE_CURRENCY = "USD"
URL_BITBAY = "https://bitbay.net/API/Public/{}{}/orderbook.json"
URL_BITFINEX = "https://api-pub.bitfinex.com/v2/ticker/t{}{}"


def get_data(url):
    raw_data = requests.get(url)
    if raw_data.status_code == 200:
        return raw_data
    return None


def get_data_bitbay(curr1, curr2):
    data = get_data(URL_BITBAY.format(curr1, curr2)).json()
    return data['bids'][0], data['asks'][0]


def get_data_bitfinex(curr1, curr2):
    try:
        data = get_data(URL_BITFINEX.format(curr1, curr2)).json()
    except AttributeError:
        pass
    return [data[0], data[1]], [data[2], data[3]]


def print_bids_asks_loop(curr1):

    exit_event = threading.Event()

    def print_loop():
        while True:
            if exit_event.isSet():
                break

            try:
                data_bitfinex = get_data_bitfinex(curr1, BASE_CURRENCY)
                data_bitbay = get_data_bitbay(curr1, BASE_CURRENCY)
            except AttributeError:
                print("API Error")
                return

            time.sleep(SLEEP)

    print("Printing bids and asks diff % for", curr1, "in a loop\nPress enter to exit the application")
    th = threading.Thread(target=print_loop)
    th.start()
    input()
    exit_event.set()
    print("Stop")


if __name__ == '__main__':
    bid, ask = get_data_bitfinex("BTC", "USD")
    print(bid, ask)
    bid, ask = get_data_bitbay("BTC", "USD")
    print(bid, ask)

