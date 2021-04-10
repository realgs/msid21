import requests
import time
import L3

#[RATE, AMOUNT]

TIME_TO_WAIT=5
CURRENCY="USD"
ARRAY=["BTC", "LTC", "ETH"]
API="https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"

def apiFormat(baseCurrency, currency):
    return API.format(baseCurrency, currency)

def jsonPrint(obj, val):
    print("---"+val+"---")
    print("BIDS:")
    i=0
    while i<3:
        print(obj["result"]['buy'][i])
        i+=1
    i=0
    print("ASKS:")
    while i<3:
        print(obj["result"]['sell'][i])
        i+=1


def getData(link: str):
    response=requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def connect():
    response1 = getData(API.format(CURRENCY, "BTC"))
    response2 = getData(API.format(CURRENCY, "BTC"))
    response3 = getData(API.format(CURRENCY, "BTC"))
    return (response1, response2, response3)

def show(response, val):
    if response is not None:
        jsonPrint(response.json(), val)

def getField(json, i, action):
    if action=="asks":
        return (json["result"]["sell"][i][1], json["result"]["sell"][i][0])
    else:
        return (json["result"]["buy"][i][1], json["result"]["buy"][i][0])

def update():
    while True:
        responses = connect()
        i=0
        while i<3:
            print(ARRAY[i])
            j=0
            while j<3:
                print("Difference: ", L3.compute(responses[i].json()["result"]['buy'][j]['Rate'], responses[i].json()["result"]['sell'][j]['Rate']))
                j+=1
            i+=1
            time.sleep(1)
        time.sleep(TIME_TO_WAIT)
