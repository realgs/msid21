import requests
import time
import Bittrex
import Bitbay
import ApiConnection

TIME_TO_WAIT=5
CURRENCY="USD"
ARRAY=["BTC", "LTC", "ETH"]

response1=ApiConnection.getData(Bitbay.apiFormat("USD", "BTC"))
response2=ApiConnection.getData(Bittrex.apiFormat("USD", "BTC"))

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def getData(link: str):
    response=requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def connectToApis():
    return (Bitbay.connect(), Bittrex.connect())


while True:
    responses = connectToApis()
    i = 0
    while i < 3:
        print(ARRAY[i])
        j = 0
        while j < 3:
            print("Difference: ",
                  compute(Bitbay.getField(responses[i].json(), j, "bids")[0], Bittrex.getField(responses[i].json(), j, "asks")[0]))
            j += 1
        i += 1
        time.sleep(1)
    time.sleep(TIME_TO_WAIT)