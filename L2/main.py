import threading
import time
import requests

REPLIES = 3


def print_bids_asks():
    data_btc = requests.get("https://bitbay.net/API/Public/BTCUSD/orderbook.json").json()
    data_ltc = requests.get("https://bitbay.net/API/Public/LTCUSD/orderbook.json").json()
    data_dash = requests.get("https://bitbay.net/API/Public/DASHUSD/orderbook.json").json()

    print("BTC bids:")
    for i in range(REPLIES):
        print(data_btc['bids'][i][0], "$")

    print("BTC asks:")
    for i in range(REPLIES):
        print(data_btc['asks'][i][0], "$")

    print("LTC bids:")
    for i in range(REPLIES):
        print(data_ltc['bids'][i][0], "$")

    print("LTC asks:")
    for i in range(REPLIES):
        print(data_ltc['asks'][i][0], "$")

    print("DASH bids:")
    for i in range(REPLIES):
        print(data_dash['bids'][i][0], "$")

    print("DASH asks:")
    for i in range(REPLIES):
        print(data_dash['asks'][i][0], "$")


def print_bids_asks_loop():

    exit_event = threading.Event()

    def print_loop():
        while True:
            if exit_event.isSet():
                break
            data_btc = requests.get("https://bitbay.net/API/Public/BTCUSD/orderbook.json").json()
            bid = data_btc['bids'][0][0]
            ask = data_btc['asks'][0][0]

            print(str((1-((ask-bid)/bid))*100)+"%")
            time.sleep(5)

    print("Printing bids and asks diff % for BTC in a loop\nPress enter to exit the aplication")
    th = threading.Thread(target=print_loop)
    th.start()
    input()
    exit_event.set()
    print("Stop")


if __name__ == '__main__':
    print_bids_asks()
    print_bids_asks_loop()
