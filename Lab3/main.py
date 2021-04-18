import requests
import time


LIMIT = 3

def main():
    calculate_price_differences()


def get_orders():
    orders = {}

    bitbay_bids = requests.get(f"https://bitbay.net/API/Public/BTCUSD/orderbook.json").json()['bids'][:LIMIT]
    bitbay_asks = requests.get(f"https://bitbay.net/API/Public/BTCUSD/orderbook.json").json()['asks'][:LIMIT]

    orders.update({'bitbay': {'bids': bitbay_bids, 'asks': bitbay_asks}})

    bittrex_orders = requests.get(f"https://api.bittrex.com/api/v1.1/public/getorderbook?market=USD-BTC&type=both").json()['result']
    bids = bittrex_orders['buy'][:LIMIT]
    bittrex_bids = []
    for b in bids:
        bittrex_bids.append([b['Rate'], b['Quantity']])

    asks = bittrex_orders['sell'][:LIMIT]
    bittrex_asks = []
    for a in asks:
        bittrex_asks.append([a['Rate'], a['Quantity']])

    orders.update({'bittrex': {'bids': bittrex_bids, 'asks': bittrex_asks}})

    return orders


def print_buy_difference(data):
    bitbay_bid_price = data['bitbay']['bids'][0][0]
    bittrex_bid_price = data['bittrex']['bids'][0][0]
    difference = abs((bitbay_bid_price - bittrex_bid_price) / bittrex_bid_price * 100)

    print(f"BUY DIFFERENCE = {difference:.3f}%")


def print_sell_difference(data):
    bitbay_aks_price = data['bitbay']['asks'][0][0]
    bittrex_aks_price = data['bittrex']['asks'][0][0]
    difference = abs((bitbay_aks_price - bittrex_aks_price) / bittrex_aks_price * 100)

    print(f"SELL DIFFERENCE = {difference:.3f}%")


def print_arbitrage(data):
    bitbay_bid_price = data['bitbay']['bids'][0][0]
    bitbay_ask_price = data['bitbay']['asks'][0][0]
    bittrex_bid_price = data['bittrex']['bids'][0][0]
    bittrex_ask_price = data['bittrex']['asks'][0][0]

    bittrex_bitbay_arbitrage = (bitbay_bid_price - bittrex_ask_price) / bittrex_ask_price * 100
    bitbay_bittrex_arbitrage = (bittrex_bid_price - bitbay_ask_price) / bitbay_ask_price * 100

    print(f"BITTREX-BITBAY ARBITRAGE = {bittrex_bitbay_arbitrage:.3f}%")
    print(f"BITBAY-BITTREX ARBITRAGE = {bitbay_bittrex_arbitrage:.3f}%")



    print()


def calculate_price_differences():
    while True:
        data = get_orders()
        print_buy_difference(data)
        print_sell_difference(data)
        print_arbitrage(data)
        # print_
        time.sleep(5)


if __name__ == '__main__':
    main()
