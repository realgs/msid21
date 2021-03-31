import requests

MARKETS = ["BTCUSD", "LTCUSD", "DASHUSD"]
PRECISION = 4
MAX_RECORDS = 20
MIN_COLUMN_SIZE = 16
TABLE_SEPARATOR = "|"




def printTableRow(bid, ask):
    print(  
        TABLE_SEPARATOR +
        f"{float(bid[0]):{MIN_COLUMN_SIZE}.{PRECISION}f}" + TABLE_SEPARATOR +
        f"{float(bid[1]):{MIN_COLUMN_SIZE}.{PRECISION}f}" + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{float(ask[0]):{MIN_COLUMN_SIZE}.{PRECISION}f}" + TABLE_SEPARATOR +
        f"{float(ask[1]):{MIN_COLUMN_SIZE}.{PRECISION}f}" + 
        TABLE_SEPARATOR
    )

def printTableHeaders():
    print(
        TABLE_SEPARATOR +
        f"{'BIDS':^{MIN_COLUMN_SIZE * 2 + len(TABLE_SEPARATOR)}}" + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{'ASKS':^{MIN_COLUMN_SIZE * 2 + len(TABLE_SEPARATOR)}}" +
        TABLE_SEPARATOR + "\n" +

        TABLE_SEPARATOR +
        f"{'Rate':^{MIN_COLUMN_SIZE}}"      + TABLE_SEPARATOR + 
        f"{'Amount':^{MIN_COLUMN_SIZE}}"    + 
        TABLE_SEPARATOR + TABLE_SEPARATOR +
        f"{'Rate':^{MIN_COLUMN_SIZE}}"      + TABLE_SEPARATOR + 
        f"{'Amount':^{MIN_COLUMN_SIZE}}"    + 
        TABLE_SEPARATOR
    )

def printOrdersTable(orders):
    printTableHeaders()
    bids = orders["bids"]
    asks = orders["asks"]
    for i in range(min(len(bids), len(asks), MAX_RECORDS)):
        printTableRow(bids[i], asks[i])
    print("\n\n")
    
def getOrders(market):
    response = requests.get(f"https://bitbay.net/API/Public/{market}/orderbook.json")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def printOrdersForEach(markets):
    for market in markets:
        orders = getOrders(market)
        if orders:
            print("\n")
            print(f"\tORDERBOOK FOR {market}:")
            printOrdersTable(orders)
        else:
            print(f"Something went wrong. Cannot get orders")
                
printOrdersForEach(MARKETS)
