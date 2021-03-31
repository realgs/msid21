import requests

BIDS = 'bids'
ASKS = 'asks'
ADDRESS_BITBAY = 'https://bitbay.net/API/Public/'
ADDRESS_ORDERBOOK = '/orderbook.json'


def print_category(category, cat_limit):
    if cat_limit > len(category):
        cat_limit = len(category)
    for i in range(0, cat_limit):
        print("Order number", i + 1, ":")
        print("rate:", category[i][0])
        print("amount:", category[i][1])


def print_orderbook(resources, bids_limit, asks_limit):
    for name in resources:
        address = ADDRESS_BITBAY + name + ADDRESS_ORDERBOOK
        response = requests.get(address)
        if response:
            response_json = response.json()

            print("\nBuy orders " + name + "\n")
            print_category(response_json[BIDS], bids_limit)

            print("\nSell orders " + name + "\n")
            print_category(response_json[ASKS], asks_limit)
        else:
            print(name, ' data not found')


def main():
    resources = ['BTCUSD', 'LTCUSD', 'DASHUSD']
    print_orderbook(resources, 5, 5)
    print_orderbook(resources, 50, 50)


if __name__ == '__main__':
    main()

