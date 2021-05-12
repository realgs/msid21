import requests
import time

#[RATE, AMOUNT]

TIME_TO_WAIT = 5
CURRENCY = "USD"
ARRAY = ["BTC", "LTC", "ETH"]
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
    response1 = getData(API.format(str(MARKETS[0]).split("-")[1], str(MARKETS[0]).split("-")[0]))
    response2 = getData(API.format(str(MARKETS[1]).split("-")[1], str(MARKETS[1]).split("-")[0]))
    response3 = getData(API.format(str(MARKETS[2]).split("-")[1], str(MARKETS[2]).split("-")[0]))
    return (response1, response2, response3)

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

def update():
    while True:
        responses = connect()
        i = 0
        while i < 3:
            print(ARRAY[i])
            j = 0
            while j < 3:
                print("Difference: ", compute(getField(responses[i].json(), j, "bids")[0], getField(responses[i].json(), j, "asks")[0]))
                j += 1
            i += 1
            time.sleep(1)
        time.sleep(TIME_TO_WAIT)


