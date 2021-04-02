import requests
import time

api = "https://bitbay.net/API/Public/"
currency = ['BTC', 'ETH', 'BSV']


def connect_with_api(curr):
        response = requests.get(api+curr+'/orderbook.json')
        if response.status_code == 200:
            return response


def print_offers(curr):
    response = connect_with_api(curr)
    r_json = response.json()

    print(f"\n{curr}")
    print("\nBids: ")
    print("price,  amount")
    for i in r_json['bids']:
        print(i)

    print(f"\n{curr}")
    print("\nAsks: ")
    print("price,  amount")
    for j in r_json['asks']:
        print(j)


def calculate_difference(curr):
    r_json = connect_with_api(curr).json()

    bids = r_json['bids']
    asks = r_json['asks']

    return (1 - (asks[0][0] - bids[0][0]) / bids[0][0]) * 100


def print_differences(curr):
    print("Difference between buying and selling: ")
    print(f"{calculate_difference(curr)}%")
    time.sleep(5)


def main():
    for c in currency:
        print_offers(c)
        print_differences(c)


if __name__ == '__main__':
    main()
