import threading
import time
import requests


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
            data_btc = requests.get("https://bitbay.net/API/Public/"+curr1+"USD/orderbook.json").json()
            bid = data_btc['bids'][0][0]
            ask = data_btc['asks'][0][0]

            print(str((1-((ask-bid)/bid))*100)+"%")
            time.sleep(5)

    print("Printing bids and asks diff % for", curr1, "in a loop\nPress enter to exit the aplication")
    th = threading.Thread(target=print_loop)
    th.start()
    input()
    exit_event.set()
    print("Stop")

# print_bids_asks_loop(curr1)


def ex1():
    replies = 3
    print_bids_asks("BTC", "USD", replies)
    print_bids_asks("LTC", "USD", replies)
    print_bids_asks("DASH", "USD", replies)

# ex1()


if __name__ == '__main__':
    ex1()
    print_bids_asks_loop("BTC")

# main
