import requests
import time

from requests import HTTPError

CURRENCY = "USD"
CRYPTOCURRENCY = "BTC"
LIMIT = 5
DELAY = 5

# BITBAY API
BITBAY_API = f"https://bitbay.net/API/Public/{CRYPTOCURRENCY}{CURRENCY}/orderbook.json"
BITBAY_TAKER = 0.0037
BITBAY_TRANSFER_FEE = 0.0005

# BITTREX API
BITTREX_API = f"https://api.bittrex.com/api/v1.1/public/getorderbook?market={CURRENCY}-{CRYPTOCURRENCY}&type=both"
BITTREX_TAKER = 0.0035
BITTREX_TRANSFER_FEE = 0.0005


def main():
    calculate_price_differences()


def calculate_price_differences():
    errors_counter = 0

    while True:
        orders_data = get_orders()

        if not orders_data:
            errors_counter += 1
            if errors_counter == 5:
                print("CONNECTION ERROR")
                break
            continue

        errors_counter = 0

        print_buy_difference(orders_data)
        print_sell_difference(orders_data)
        print_arbitrage(orders_data)

        time.sleep(DELAY)


def get_orders():
    orders = {}

    try:
        response = requests.get(BITBAY_API)

        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

    bitbay_orders = response.json()

    bitbay_bids = bitbay_orders['bids'][:LIMIT]
    bitbay_asks = bitbay_orders['asks'][:LIMIT]

    orders.update({'bitbay': {'bids': bitbay_bids, 'asks': bitbay_asks}})

    try:
        response = requests.get(BITTREX_API)

        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

    bittrex_orders = response.json()['result']

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


def print_buy_difference(orders_data):
    bitbay_bid_price = orders_data['bitbay']['bids'][0][0]
    bittrex_bid_price = orders_data['bittrex']['bids'][0][0]
    difference = abs(calculate_percentage_difference(bitbay_bid_price, bittrex_bid_price))

    print(f"BUY DIFFERENCE = {difference:.3f}%")


def calculate_percentage_difference(number1, number2):
    return (number1 - number2) / number2 * 100


def print_sell_difference(orders_data):
    bitbay_aks_price = orders_data['bitbay']['asks'][0][0]
    bittrex_aks_price = orders_data['bittrex']['asks'][0][0]
    difference = abs(calculate_percentage_difference(bitbay_aks_price, bittrex_aks_price))

    print(f"SELL DIFFERENCE = {difference:.3f}%")


def print_arbitrage(orders_data):
    print("\n# WITHOUT FEES")
    print_arbitrage_without_fees(orders_data, 'bittrex', 'bitbay')
    print_arbitrage_without_fees(orders_data, 'bitbay', 'bittrex')

    print("\n# WITH FEES")
    print_arbitrage_wit_fees(orders_data, 'bittrex', 'bitbay', BITTREX_TAKER, BITTREX_TRANSFER_FEE)
    print_arbitrage_wit_fees(orders_data, 'bitbay', 'bittrex', BITBAY_TAKER, BITBAY_TRANSFER_FEE)


def print_arbitrage_without_fees(orders_data, exchange1, exchange2):
    exchange1_ask_price = orders_data[exchange1]['asks'][0][0]
    exchange2_bid_price = orders_data[exchange2]['bids'][0][0]

    arbitrage = calculate_percentage_difference(exchange2_bid_price, exchange1_ask_price)

    print(f"{exchange1.upper()}-{exchange2.upper()} ARBITRAGE = {arbitrage:.3f}%")


def print_arbitrage_wit_fees(orders_data, exchange1, exchange2, exchange1_taker, exchange1_transfer_fee):
    exchange1_best_ask = orders_data[exchange1]['asks'][0]
    exchange1_ask_price = exchange1_best_ask[0]
    exchange1_volume = exchange1_best_ask[1]

    exchange2_best_bid = orders_data[exchange2]['bids'][0]
    exchange2_bid_price = exchange2_best_bid[0]
    exchange2_volume = exchange2_best_bid[1]

    min_volume = min(exchange1_volume, exchange2_volume)

    volume_minus_fees = min_volume * (1 - exchange1_taker) - exchange1_transfer_fee

    exchange1_price = min_volume * exchange1_ask_price
    exchange2_price = volume_minus_fees * exchange2_bid_price

    profit = exchange2_price - exchange1_price

    print(f"# {exchange1.upper()}-{exchange2.upper()}")
    print(f"{CRYPTOCURRENCY} VOLUME = {min_volume} BTC")
    print(f"PERCENT PROFIT = {profit / exchange1_price * 100:.2f}%")
    print(f"{CURRENCY} PROFIT = {profit:.2f} USD\n")


if __name__ == '__main__':
    main()
