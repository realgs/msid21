import requests
import time

MARKETS = ["BTCUSD", "LTCUSD", "DASHUSD"]
PRECISION = 1
MAX_RECORDS = 8
MIN_COLUMN_SIZE = 16
TABLE_SEPARATOR = " |"

def printTableRow(rateDiff):
    print(  
        TABLE_SEPARATOR +
        f"{rateDiff * 100:{MIN_COLUMN_SIZE}.{PRECISION}f}%" +
        TABLE_SEPARATOR
    )

def calculateRateDiff(sellRate, buyRate):
    return 1 - (sellRate - buyRate) / buyRate

def printRatesDiffTable(orders):
    bids = orders["bids"]
    asks = orders["asks"]
    for i in range(min(len(bids), len(asks), MAX_RECORDS)):
        printTableRow(calculateRateDiff(bids[i][0], asks[i][0]))    

def getOrders(market):
    response = requests.get(f"https://bitbay.net/API/Public/{market}/orderbook.json")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def printRatesDiffForEach(markets):
    for market in markets:
        orders = getOrders(market)
        if orders:
            print("\n")
            print(f"\tORDERS RATIO DIFF FOR {market}:")
            printRatesDiffTable(orders)
        else:
            print(f"Something went wrong. Cannot get orders")

def startPrintLoop():
    while True:
        printRatesDiffForEach(MARKETS)
        print("-----------------------------------------")
        time.sleep(5)

startPrintLoop()






