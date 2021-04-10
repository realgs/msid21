import requests
import time

TIME_TO_WAIT=5
CURRENCY="USD"
ARRAY=["BTC", "LTC", "DASH"]

API="https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"
res=requests.get("https://api.bittrex.com/api/v1.1/public/getorderbook?market=USD-BTC&type=both")

print(res.json())

def jprint(obj, val):
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
    response1=getData(API.format("BTC", CURRENCY))
    response2 = getData(API.format("LTC", CURRENCY))
    response3 = getData(API.format("DASH", CURRENCY))
    return (response1, response2, response3)

def show(response, val):
    if response is not None:
        jprint(response.json(), val)

show(getData(API.format(CURRENCY, "BTC")), "BTC")
show(getData(API.format(CURRENCY, "LTC")), "LTC")
show(getData(API.format(CURRENCY, "DASH")), "DASH")

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
                print("Difference: ", compute(responses[i].json()['buy'][j][0], responses[i].json()['sell'][j][0]))
                j+=1
            i+=1
            time.sleep(1)
        time.sleep(TIME_TO_WAIT)

update()