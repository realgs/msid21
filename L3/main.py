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
    data = get_data(URL_BITFINEX.format(curr1, curr2)).json()
    return [data[0], data[1]], [data[2], data[3]]


def print_bids_asks_loop(curr1):
    exit_event = threading.Event()

    def print_loop():
        while True:
            if exit_event.isSet():
                break

            try:
                bid_bitfinex, ask_bitfinex = get_data_bitfinex(curr1, BASE_CURRENCY)
                bid_bitbay, ask_bitbay = get_data_bitbay(curr1, BASE_CURRENCY)
            except AttributeError:
                print("API Error")
                return

            # asks % diff
            print("Lowest {} ask difference in %, BitFinex to BitBay".format(curr1))
            print(str((ask_bitfinex[0] - ask_bitbay[0]) / ask_bitfinex[0] * 100) + "%")

            # bids % diff
            print("Highest {} bid difference in %, BitFinex to BitBay".format(curr1))
            print(str((bid_bitfinex[0] - bid_bitbay[0]) / bid_bitfinex[0] * 100) + "%")

            # bid to sell % diff
            bitfinex_to_bitbay = (bid_bitfinex[0] - ask_bitbay[0]) / bid_bitfinex[0]
            bitbay_to_bitfinex = (bid_bitbay[0] - ask_bitfinex[0]) / bid_bitbay[0]

            print("Buying {} on BitFinex to selling on BitBay".format(curr1))
            print(str(bitfinex_to_bitbay * 100) + "%")

            print("Buying {} on BitBay to selling on BitFinex".format(curr1))
            print(str(bitbay_to_bitfinex * 100) + "%")

            time.sleep(SLEEP)

    th = threading.Thread(target=print_loop)
    th.start()
    input()
    exit_event.set()
    print("Stop")


if __name__ == '__main__':
    print_bids_asks_loop("BTC")
