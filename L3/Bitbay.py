import requests
import time

TIME_TO_WAIT=5
API="https://bitbay.net/API/Public/{}{}/orderbook.json"
CURRENCY="USD"
ARRAY=["BTC", "LTC", "DASH"]

SNDAPI="https://api.bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both"
res=requests.get("https://api.bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both")

def jprint(obj, val):
    print("---"+val+"---")
    print("BIDS:")
    i=0
    while i<3:
        print(obj["bids"][i])
        i+=1
    i=0
    print("ASKS:")
    while i<3:
        print(obj["asks"][i])
        i+=1


def getData(link: str):
    response=requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def connect():
    response1=getData(API.format("BTC", CURRENCY))
    response2 = getData(API.format("LTC", CURRENCY))
    response3 = getData(API.format("DASH", CURRENCY))
    return (response1, response2, response3)

def show(response, val):
    if response is not None:
        jprint(response.json(), val)

show(getData(API.format("BTC", CURRENCY)), "BTC")
show(getData(API.format("LTC", CURRENCY)), "LTC")
show(getData(API.format("DASH", CURRENCY)), "DASH")

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def update():
    while True:
        responses = connect()
        i=0
        while i<3:
            print(ARRAY[i])
            j=0
            while j<3:
                print("Difference: ", compute(responses[i].json()["bids"][j][0], responses[i].json()["asks"][j][0]))
                j+=1
            i+=1
            time.sleep(1)
        time.sleep(TIME_TO_WAIT)

update()