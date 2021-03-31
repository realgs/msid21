import requests

def print_order_book(currencies):
    response = requests.get("https://bitbay.net/API/Public/" + currencies + "/orderbook.json")
    response = response.json()
    bids = response.get('bids', 'There are no bids!')
    asks = response.get('asks', 'There are no asks!')
    print("PRINTING FOR CURRENCIES " + currencies + ": ")
    print("Bids:")
    print(bids)
    print()
    print("Asks:")
    print(asks)
    print()

print_order_book("BTCUSD")
print_order_book("LTCUSD")
print_order_book("DASHUSD")

