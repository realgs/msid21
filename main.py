import time
import requests

BTC = 'BTC'
BASE_CURRENCY = 'USD'
BITBAY_URL = "https://bitbay.net/API/Public/{}/orderbook.json".format(BTC + BASE_CURRENCY)
BITTREX_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(BASE_CURRENCY, BTC)
FEES = {"bitbay": {"taker": 0.0043, "transfer": 0.0005},
        "bittrex": {"taker": 0.0075, "transfer": 0.0005}}
DELAY = 5
ROUND = 3
CONNECTION_FAILED = "Connection failed"
markets = ['bitbay', 'bittrex']


def connect_with_api(api):
    try:
        response = requests.get(api)
        if response.status_code in range(200, 299):
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print(CONNECTION_FAILED)
        return None


def get_bitbay_data(response):
    bids_bitbay = response['bids']
    asks_bitbay = response['asks']

    return bids_bitbay[0][0], bids_bitbay[0][1], asks_bitbay[0][0], asks_bitbay[0][1]


def get_bittrex_data(response):
    bids_bittrex = response['result']['buy']
    asks_bittrex = response['result']['sell']

    return bids_bittrex[0]['Rate'], bids_bittrex[0]['Quantity'], asks_bittrex[0]['Rate'], asks_bittrex[0]['Quantity']


def calculate_percentage_difference(price1, price2):
    return round((1 - (price1 - price2)) / price2 * 100, ROUND)


def arbitrage(ask, bid, ask_taker_fee, bid_taker_fee, ask_transfer_fee, bid_transfer_fee):
    transaction_volume = min(ask[3], bid[1])
    buying_price = transaction_volume * ask[2]
    selling_price = transaction_volume * bid[0]
    buying_fee = buying_price * ask_taker_fee + ask_transfer_fee * ask[2]
    selling_fee = selling_price * bid_taker_fee + bid_transfer_fee * bid[0]

    total_fee = selling_fee + buying_fee
    profit = selling_price - buying_price - total_fee

    return transaction_volume, profit, buying_price, total_fee


def print_arbitrage(data):
    print(f"Arbitrage volume: {data[0]}")
    print(f"Profit: {round(data[1] / (data[2] + data[3]) * 100, ROUND)}%")
    print(f"Profit in {BASE_CURRENCY}: {round(data[1], ROUND)} {BASE_CURRENCY}")


def print_differences(bitbay_data, bittrex_data):
    while True:
        bitbay = get_bitbay_data(bitbay_data)
        bittrex = get_bittrex_data(bittrex_data)

        print(f"Buying prices in {markets[0]} and {markets[1]} difference: "
              f"{abs(calculate_percentage_difference(bitbay[0], bittrex[0]))}%")
        print(f"Selling prices in {markets[0]} and {markets[1]} difference: "
              f"{abs(calculate_percentage_difference(bitbay[2], bittrex[2]))}%")
        print()
        print(f"Buying price in {markets[0]} to selling price in {markets[1]}: "
              f"{calculate_percentage_difference(bitbay[2], bittrex[0])}")
        print_arbitrage(arbitrage(bitbay, bittrex, FEES['bitbay']['taker'], FEES['bittrex']['taker'],
                        FEES['bitbay']['transfer'], FEES['bittrex']['transfer']))
        print()
        print(f"Buying price in {markets[1]} to selling price in {markets[0]}: "
              f"{calculate_percentage_difference(bittrex[2], bitbay[0])}")
        print_arbitrage(arbitrage(bittrex, bitbay, FEES['bittrex']['taker'], FEES['bitbay']['taker'],
                        FEES['bittrex']['transfer'], FEES['bitbay']['transfer']))

        time.sleep(DELAY)


if __name__ == '__main__':
    response_bitbay = connect_with_api(BITBAY_URL)
    response_bittrex = connect_with_api(BITTREX_URL)

    if response_bitbay and response_bittrex:
        print_differences(response_bitbay, response_bittrex)
