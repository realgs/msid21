import requests

BIDS = 'bids'
ASKS = 'asks'
ADDRESS_BITBAY = 'https://bitbay.net/API/Public/'
ADDRESS_ORDERBOOK = '/orderbook.json'
BASE_CURRENCY = 'USD'


def get_data(currencies):
    address = ADDRESS_BITBAY + currencies + ADDRESS_ORDERBOOK
    return requests.get(address)


def print_category(category, cat_limit):
    if cat_limit > len(category):
        cat_limit = len(category)
    for i in range(0, cat_limit):
        print("Order number", i + 1, ":")
        print("rate:", category[i][0])
        print("amount:", category[i][1])


def print_orderbook(resources, bids_limit, asks_limit):
    for crypto_currency in resources:
        currencies = crypto_currency + BASE_CURRENCY
        response = get_data(currencies)
        if response:
            response_json = response.json()

            print("\nBuy orders " + currencies + "\n")
            print_category(response_json[BIDS], bids_limit)

            print("\nSell orders " + currencies + "\n")
            print_category(response_json[ASKS], asks_limit)
        else:
            print(currencies, ' data not found')


def main():
    resources = ['BTC', 'LTC', 'DASH']
    print_orderbook(resources, 5, 5)
    print_orderbook(resources, 50, 50)


if __name__ == '__main__':
    main()

