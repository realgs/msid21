import requests

api = "https://bitbay.net/API/Public/"
currency = ['BTC', 'ETH', 'BSV']


def connect_with_api():
    for c in currency:
        response = requests.get(api+c+'/orderbook.json')
        if response.status_code == 200:
            print_offers(response, c)
        else:
            print("Connection failed")


def print_offers(response, currency):
    r_json = response.json()

    print(f"\n{currency}")
    print("\nBids: ")
    print("price,  amount")
    for i in r_json['bids']:
        print(i)

    print(f"\n{currency}")
    print("\nAsks: ")
    print("price,  amount")
    for j in r_json['asks']:
        print(j)


def main():
    connect_with_api()


if __name__ == '__main__':
    main()
