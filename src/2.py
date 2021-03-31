import requests
import time

def printPercentages(currencies):
    for currency in currencies:
        r = requests.get(f"https://bitbay.net/API/Public/{currency}/orderbook.json")
        r = r.json()

        print(currency + ": ")
        print((1 - (r["asks"][0][0] - r["bids"][0][0]) / r["bids"][0][0]) * 100, "%", sep='')

def setDaemon():
    currencies = ["DASHUSD", "BTCUSD", "LTCUSD"]
    while True:
        printPercentages(currencies)
        print()
        time.sleep(5)

# main
setDaemon()