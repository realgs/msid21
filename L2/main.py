from pip._vendor import requests

REPLIES = 3


def print_bids_asks():
    data_btc = requests.get("https://bitbay.net/API/Public/BTCUSD/orderbook.json").json()
    data_ltc = requests.get("https://bitbay.net/API/Public/LTCUSD/orderbook.json").json()
    data_dash = requests.get("https://bitbay.net/API/Public/DASHUSD/orderbook.json").json()

    print("BTC bids:")
    for i in range(REPLIES):
        print(data_btc['bids'][i])

    print("BTC asks:")
    for i in range(REPLIES):
        print(data_btc['asks'][i])

    print("LTC bids:")
    for i in range(REPLIES):
        print(data_ltc['bids'][i])

    print("LTC asks:")
    for i in range(REPLIES):
        print(data_ltc['asks'][i])

    print("DASH bids:")
    for i in range(REPLIES):
        print(data_dash['bids'][i])

    print("DASH asks:")
    for i in range(REPLIES):
        print(data_dash['asks'][i])

print_bids_asks()