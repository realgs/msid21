import requests

def printCur(currencies):
    for currency in currencies:
        r = requests.get(f"https://bitbay.net/API/Public/{currency}/orderbook.json")
        r = r.json()

        print("---------" + currency + "---------")
        print("Bids:")
        for bid in r["bids"]:
            print(bid)
        
        print("\nAsks")
        for ask in r["asks"]:
            print(ask)
        print()
        

# main
currencies = ["DASHUSD", "BTCUSD", "LTCUSD"]
printCur(currencies)