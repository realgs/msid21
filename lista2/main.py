import requests
import time

def getOffers():
    print(getOfferList("BTC").json())
    print(getOfferList("LTC").json())
    print(getOfferList("DASH").json())


def getOfferList(name):
    return requests.get("https://bitbay.net/API/Public/" + name + "/orderbook.json")


def calculate(offers):
    for offer in offers:
        s = str(offer.json().keys())
        if s.__contains__("code"):
            print("error")
        else:
            bids = offer.json()['bids']
            asks = offer.json()['asks']
            res = (1 - (asks[0][0] - bids[0][0]) / bids[0][0]) * 100
            print(str(res) + "%")


if __name__ == '__main__':

    print("zadanie 1: ")
    getOffers()

    print("zadanie 2: ")
    while True:
        btc = getOfferList("BTC")
        ltc = getOfferList("LTC")
        dash = getOfferList("DASH")
        calculate([btc, ltc, dash])
        print("----------------------------")
        time.sleep(5)
