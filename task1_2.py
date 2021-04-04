import time
import requests

BIDS = 'bids'
ASKS = 'asks'
BUY = 'buy'
SELL = 'sell'
QUANTITY = 'Quantity'
RATE = 'Rate'
QUANTITY_CODE = 1
RATE_CODE = 0
RESULT = 'result'
ADDRESS_BITBAY = 'https://bitbay.net/API/Public/'
RESPONSE_TYPE_ORDERBOOK_BITBAY = '/orderbook.json'
ADDRESS_BITTREX = 'https://api.bittrex.com/api/v1.1/public/'
RESPONSE_TYPE_ORDERBOOK_BITTREX = 'getorderbook?market='
ORDERBOOK_TYPE = '&type=both'
TAKER_BITBAY = 0.42  # in %, with condition: 30-Day Volume ($0-$4400)
TAKER_BITTREX = 0.75  # in %, with condition: 30-Day Volume ($0-$5K)
TRANSFER_FEE_BTC_BITBAY = 0.0005  # in BTC
TRANSFER_FEE_BTC_BITTREX = 0.0005  # in BTC
BASE_CURRENCY = 'USD'
ARBITRAGE_BITTREX_BITBAY_CODE = 0
ARBITRAGE_BITBAY_BITTREX_CODE = 1


def get_bitbay_json(currencies):
    try:
        response = requests.get(ADDRESS_BITBAY + currencies + RESPONSE_TYPE_ORDERBOOK_BITBAY)
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Connection to api failed", response.reason)
        return None


def get_bittrex_json(currencies):
    try:
        response = requests.get(ADDRESS_BITTREX + RESPONSE_TYPE_ORDERBOOK_BITTREX + currencies + ORDERBOOK_TYPE)
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Connection to api falied", response.reason)
        return None


def get_bitbay_data(response, bids_or_asks, quantity_or_rate):
    return response[bids_or_asks][0][quantity_or_rate]


def get_bittrex_data(response, sell_or_buy, quantity_or_rate):
    return response[RESULT][sell_or_buy][0][quantity_or_rate]


def get_percentage_difference(first, second):
    return (1 - (first - second) / second) * 100


def get_arbitrage(arbitrage_code, response_bitbay, response_bittrex):
    if arbitrage_code == 0:
        bittrex_type = SELL
        bitbay_type = BIDS
    elif arbitrage_code == 1:
        bittrex_type = BUY
        bitbay_type = ASKS
    else:
        print("invalid arbitrage_code")
        return None

    bittrex_quantity = get_bittrex_data(response_bittrex, bittrex_type, QUANTITY)
    bittrex_rate = get_bittrex_data(response_bittrex, bittrex_type, RATE)
    bitbay_quantity = get_bitbay_data(response_bitbay, bitbay_type, QUANTITY_CODE)
    bitbay_rate = get_bitbay_data(response_bitbay, bitbay_type, RATE_CODE)
    transaction_quantity = min(bittrex_quantity, bitbay_quantity)

    if arbitrage_code == 0:
        payment = bittrex_rate * transaction_quantity * (1 + TAKER_BITTREX / 100) + TRANSFER_FEE_BTC_BITTREX
        profit = bitbay_rate * transaction_quantity * (1 - TAKER_BITBAY / 100)
    elif arbitrage_code == 1:
        payment = bitbay_rate * transaction_quantity * (1 + TAKER_BITBAY / 100) + TRANSFER_FEE_BTC_BITBAY
        profit = bittrex_rate * transaction_quantity * (1 - TAKER_BITTREX / 100)

    return [transaction_quantity, payment, profit]


def print_difference(crypto_currency):
    response_bitbay = get_bitbay_json(crypto_currency + BASE_CURRENCY)
    response_bittrex = get_bittrex_json(BASE_CURRENCY + "-" + crypto_currency)
    if response_bittrex is not None and response_bitbay is not None:
        sells_bittrex = get_bittrex_data(response_bittrex, BUY, RATE)
        buys_bittrex = get_bittrex_data(response_bittrex, SELL, RATE)
        print(buys_bittrex, sells_bittrex)
        sells_bitbay = get_bitbay_data(response_bitbay, BIDS, RATE_CODE)
        buys_bitbay = get_bitbay_data(response_bitbay, ASKS, RATE_CODE)
        print(buys_bitbay, sells_bitbay)
        print("diff bittrex-bitbay buy: ", get_percentage_difference(buys_bitbay, buys_bittrex), "%", sep="")
        print("diff bittrex-bitbay sell: ", get_percentage_difference(sells_bitbay, sells_bittrex), "%", sep="")
        print("diff bitbay-buy bittrex-sell: ", get_percentage_difference(buys_bitbay, sells_bittrex), "%", sep="")
        print("diff bittrex-buy bitbay-sell: ", get_percentage_difference(buys_bittrex, sells_bitbay), "%", sep="")

        transaction_quantity, payment, profit = get_arbitrage(ARBITRAGE_BITTREX_BITBAY_CODE, response_bitbay,
                                                              response_bittrex)
        print("quantity:", transaction_quantity, ", payment:", payment, ", profit:", profit)
        print("Earning in %:", get_percentage_difference(payment, profit))
        print("Earning in USD:", profit - payment)
    else:
        print("data not found")


def print_updating_diff(crypto_currency, delay):
    while True:
        print_difference(crypto_currency)
        time.sleep(delay)


def main():
    print_difference('BTC')


if __name__ == '__main__':
    main()

