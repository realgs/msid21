import requests

BIDS = 'bids'
ASKS = 'asks'


def print_orderbook(resources, bids_limit, asks_limit):
    for name in resources:
        address = 'https://bitbay.net/API/Public/' + name + '/orderbook.json'
        response = requests.get(address)
        if response:
            response_json = response.json()

            print("\nBuy orders " + name + "\n")
            if bids_limit > len(response_json[BIDS]):
                bids_limit = len(response_json[BIDS])
            for i in range(0, bids_limit):
                print("Order number", i + 1, ":")
                print("rate:", response_json[BIDS][i][0])
                print("amount:", response_json[BIDS][i][1])

            print("\nSell orders " + name + "\n")
            if asks_limit > len(response_json[ASKS]):
                asks_limit = len(response_json[ASKS])
            for i in range(0, asks_limit):
                print("Order number", i + 1, ":")
                print("rate:", response_json[ASKS][i][0])
                print("amount:", response_json[ASKS][i][1])
        else:
            print(name, ' data not found')


resources = ['BTCUSD', 'LTCUSD', 'DASHUSD']
print_orderbook(resources, 5, 5)
