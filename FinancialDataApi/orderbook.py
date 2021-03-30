import requests

COLUMN_SIZE = 16
PRECISION = 4
MARKETS = ["BTCUSD", "LTCUSD", "DASHUSD"]
TABLE_SEPARATOR = "|"
MAX_RECORDS = 20

def printTableHeaders():
    print(
        TABLE_SEPARATOR +
        f"{'BIDS':^{COLUMN_SIZE * 2 + len(TABLE_SEPARATOR)}}" + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{'ASKS':^{COLUMN_SIZE * 2 + len(TABLE_SEPARATOR)}}" +
        TABLE_SEPARATOR + "\n" +

        TABLE_SEPARATOR +
        f"{'Rate':^{COLUMN_SIZE}}"      + TABLE_SEPARATOR + 
        f"{'Amount':^{COLUMN_SIZE}}"    + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{'Rate':^{COLUMN_SIZE}}"      + TABLE_SEPARATOR + 
        f"{'Amount':^{COLUMN_SIZE}}"    + 
        TABLE_SEPARATOR
    )

def printTableRow(bid, ask):
    print(  
        TABLE_SEPARATOR +
        f"{float(bid[0]):{COLUMN_SIZE}.{PRECISION}f}" + TABLE_SEPARATOR +
        f"{float(bid[1]):{COLUMN_SIZE}.{PRECISION}f}" + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{float(ask[0]):{COLUMN_SIZE}.{PRECISION}f}" + TABLE_SEPARATOR +
        f"{float(ask[1]):{COLUMN_SIZE}.{PRECISION}f}" + 
        TABLE_SEPARATOR
    )

def printMarket(market):
    response = requests.get(f"https://bitbay.net/API/Public/{market}/orderbook.json")
    if response.status_code == 200:
        printTableHeaders()
        bids = response.json()["bids"]
        asks = response.json()["asks"]
        for i in range(min(len(bids), len(asks), MAX_RECORDS)):
            printTableRow(bids[i], asks[i])
        print("\n\n")
    else:
        print(f"Something went wrong (response is : {response.status_code}")

def printAllMarkets(markets):
    for market in markets:
        print(f"\tORDERBOOK FOR {market}:")
        printMarket(market)

printAllMarkets(MARKETS)
