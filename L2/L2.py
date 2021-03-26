import requests
import time

#ZADANIE 1
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

def connect():
    response1=requests.get("https://bitbay.net/API/Public/BTCUSD/orderbook.json")
    response2 = requests.get("https://bitbay.net/API/Public/LTCUSD/orderbook.json")
    response3 = requests.get("https://bitbay.net/API/Public/DASHUSD/orderbook.json")
    return(response1, response2, response3)

def show(responses):
    jprint((responses[0]).json(), "BTC")
    jprint(responses[1].json(), "LTC")
    jprint(responses[2].json(), "DASH")

show(connect())

#ZADANIE 2
def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def update():
    while True:
        responses = connect()
        i=0
        while i<3:
            if i==0:
                print("---BTC---")
            elif i==1:
                print("---LTC---")
            else:
                print("---DASH---")
            j=0
            while j<3:
                print("Difference: ", compute(responses[i].json()["bids"][j][0], responses[i].json()["asks"][j][0]))
                j+=1
            i+=1
            time.sleep(1)
        time.sleep(5)

update()