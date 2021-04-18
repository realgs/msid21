import requests
import time

BITBAY_TAKER = 0.0037
BITBAY_TRANSFER_FEE = 0.0005
BITTREX_TAKER = 0.0035
BITTREX_TRANSFER_FEE = 0.0005
LIMIT = 1


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

    bitbay_volume = data['bitbay']['bids'][0][1]
    bittrex_volume = data['bittrex']['asks'][0][1]

    volume = min(bitbay_volume, bittrex_volume)
    real_volume = volume * (1 - BITTREX_TAKER) - BITTREX_TRANSFER_FEE
    bittrex_price = volume * bittrex_ask_price
    bitbay_price = real_volume * bitbay_bid_price

    profit = bitbay_price - bittrex_price

    print(f"VOLUME = {volume} BTC")
    print(f"PERCENT PROFIT = {profit / bittrex_price * 100:.2f}%")
    print(f"PROFIT = {profit:.2f} USD")

    print()


def calculate_price_differences():
    while True:
        data = get_orders()
        print_buy_difference(data)
        print_sell_difference(data)
        print_arbitrage(data)
        time.sleep(5)


if __name__ == '__main__':
    main()
