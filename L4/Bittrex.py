import requests
import time

#[RATE, AMOUNT]

TIME_TO_WAIT = 5
API = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"

MARKETS = []

markets = set()

def apiFormat(baseCurrency, currency):
    return API.format(baseCurrency, currency)

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def jsonPrint(obj, val):
    print("---"+val+"---")
    print("BIDS:")
    i = 0
    while i < 3:
        print(obj["result"]['buy'][i])
        i += 1
    i = 0
    print("ASKS:")
    while i < 3:
        print(obj["result"]['sell'][i])
        i += 1

def getData(link: str):
    response = requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def connect():
    responses = []
    i = 0
    while i < len(MARKETS):
        responses.append(getData(API.format(str(MARKETS[i]).split("-")[1], str(MARKETS[i]).split("-")[0])))
        i += 1
    return tuple(responses)

def show(response, val):
    if response is not None:
        jsonPrint(response.json(), val)

def getAllMarkets():
    response = getData("https://api.bittrex.com/api/v1.1/public/getmarkets")
    results = response.json()["result"]
    for r in results:
        markets.add(r["MarketCurrency"] + "-" + r["BaseCurrency"])

def getTicker():
    response = getData("https://api.bittrex.com/api/v1.1/public/getmarkets")
    return response.json()

def getOrdersNumber(json):
    l1 = len(json["result"]["buy"])
    l2 = len(json["result"]["sell"])
    if l1 > l2:
        return l2
    else:
        return l1

def getField(json, i, action):
    if action == "asks":
        return (json["result"]["sell"][i]['Rate'], json["result"]["sell"][i]['Quantity'])
    else:
        return (json["result"]["buy"][i]['Rate'], json["result"]["buy"][i]['Quantity'])