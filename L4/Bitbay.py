import requests
import time

TIME_TO_WAIT = 5
API = "https://bitbay.net/API/Public/{}{}/orderbook.json"

MARKETS = []

markets = set()

def apiFormat(baseCurrency, currency):
    return API.format(currency, baseCurrency)

def jsonPrint(obj, val):
    print("---"+val+"---")
    print("BIDS:")
    i = 0
    while i < 3:
        print(obj["bids"][i])
        i += 1
    i = 0
    print("ASKS:")
    while i < 3:
        print(obj["asks"][i])
        i += 1

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def getData(link: str):
    response = requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def connect():
    responses = []
    i = 0
    while i < len(MARKETS):
        responses.append(getData(API.format(str(MARKETS[i]).split("-")[0], str(MARKETS[i]).split("-")[1])))
        i += 1
    return tuple(responses)

def show(response, val):
    if response is not None:
        jsonPrint(response.json(), val)


def getField(json, i, action):
    if action == "asks":
        return (json["asks"][i][0], json["asks"][i][1])
    else:
        return (json["bids"][i][0], json["bids"][i][1])

def getAllMarkets():
    response = getData("https://api.bitbay.net/rest/trading/ticker")
    results = response.json()["items"]
    for k in results:
        markets.add(k)

def getTicker():
    response = getData("https://api.bitbay.net/rest/trading/ticker")
    return response.json()

def getOrdersNumber(json):
    l1 = len(json["bids"])
    l2 = len(json["asks"])
    if l1 > l2:
        return l2
    else:
        return l1
