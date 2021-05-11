import time
import requests

SLEEP = 5

API = 'https://bitbay.net/API/Public/'

def zadanie1(currencies, curr, limit):
    for data in currencies:
        req = requests.get(API+data+curr+'/orderbook.json')
        req = req.json()

        print("         " + data + "        ")
        print("BUY:")
        for buy in req["bids"][:limit]:
            print(buy)

        print("\nSELL")
        for sell in req["asks"][:limit]:
            print(sell)
        print()

def countPerc(currencies, curr):
    for data in currencies:
        req = requests.get(API+data+curr+'/orderbook.json')
        req = req.json()

        print(data+":  ")
        print(1 - (req["asks"][0][0] - req["bids"][0][0]) / req["bids"][0][0] * 100, "%\n")

def zadanie2(currencies, curr):
    while True:
        countPerc(currencies, curr)
        print()
        time.sleep(SLEEP)


if __name__ == '__main__':
    currencies = ["BTC", "LTC", "DASH"]
    zadanie1(currencies, "USD", 5) #zadanie1
    zadanie2(currencies, "USD") #zadanie2