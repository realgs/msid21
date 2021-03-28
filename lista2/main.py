import requests


def getOffers():
    btc = getOfferList("BTC")
    ltc = getOfferList("LTC")
    dash = getOfferList("DASH")
    print(btc.json())
    print(ltc.json())
    print(dash.json())


def getOfferList(name):
    return requests.get("https://bitbay.net/API/Public/" + name + "/orderbook.json")


if __name__ == '__main__':
    getOffers()
