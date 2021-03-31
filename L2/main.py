import threading
import time
import requests

SLEEP = 5
REPLIES = 3
BASE_CURRENCY = "USD"


def print_bids_asks(curr1, curr2, replies):
    data = requests.get("https://bitbay.net/API/Public/"+curr1+curr2+"/orderbook.json").json()

    print(curr1, "bids:")
    for i in range(replies):
        print(data['bids'][i][0], curr2)

    print(curr1, "asks:")
    for i in range(replies):
        print(data['asks'][i][0], curr2)

# print_bids_asks(curr1, curr2, replies)


def print_bids_asks_loop(curr1):

    exit_event = threading.Event()

    def print_loop():
        while True:
            if exit_event.isSet():
                break
            data_btc = requests.get("https://bitbay.net/API/Public/"+curr1+BASE_CURRENCY+"/orderbook.json").json()
            bid = data_btc['bids'][0][0]
            ask = data_btc['asks'][0][0]

            print(str((1-((ask-bid)/bid))*100)+"%")
            time.sleep(SLEEP)

    # print_loop()

    print("Printing bids and asks diff % for", curr1, "in a loop\nPress enter to exit the aplication")
    th = threading.Thread(target=print_loop)
    th.start()
    input()
    exit_event.set()
    print("Stop")

# print_bids_asks_loop(curr1)


def ex1():
    print_bids_asks("BTC", BASE_CURRENCY, REPLIES)
    print_bids_asks("LTC", BASE_CURRENCY, REPLIES)
    print_bids_asks("DASH", BASE_CURRENCY, REPLIES)

# ex1()


if __name__ == '__main__':
    ex1()
    print_bids_asks_loop("BTC")

# main
