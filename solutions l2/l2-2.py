import requests
import time

#(cena sprzedaży - cena kupna) / cena kupna

def diffsellbuy(currencies):
    response = requests.get("https://bitbay.net/API/Public/" + currencies + "/orderbook.json")
    response = response.json()
    bids = response.get('bids', 'There are no bids!')
    asks = response.get('asks', 'There are no asks!')
    (buyprice, bidq) = bids[0]
    (sellprice, askq) = asks[0]
    percentage = "{:.2%}".format((sellprice-buyprice)/buyprice)
    return percentage

def monitor(currencies):
    print("Monitoring difference betweend sell and buy prices for " + currencies + ": ")
    while True:
        print(diffsellbuy(currencies))
        time.sleep(5)

monitor("BTCUSD")