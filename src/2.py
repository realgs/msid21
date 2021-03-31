import requests
import time

SLEEPTIME = 5

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
        time.sleep(SLEEPTIME)

# main
setDaemon()