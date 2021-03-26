import requests

def jprint(obj, val):
    print("---"+val+"---")
    print("BIDS:")
    print(obj["bids"][0], obj["bids"][1], obj["bids"][2])
    print("ASKS:")
    print(obj["asks"][0], obj["asks"][1], obj["asks"][2])

def connect():
    response=requests.get("https://bitbay.net/API/Public/BTCUSD/orderbook.json")
    jprint(response.json(), "BTC")
    response = requests.get("https://bitbay.net/API/Public/LTCUSD/orderbook.json")
    jprint(response.json(), "LTC")
    response = requests.get("https://bitbay.net/API/Public/DASHUSD/orderbook.json")
    jprint(response.json(), "DASH")

connect()