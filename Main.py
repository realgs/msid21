import time

from BitBayAPI import BitBayAPI
from BittRexAPI import BittRexAPI

CRYPTO_CURRENCY = "BTC"
BASE_CURRENCY = "USD"
SLEEP_TIME = 5


def exc_1(bitt_rex, bit_bay, crypto_currency, base_currency, abc):
    print("EXC 1")
    if abc == 'a':
        print("Difference for buying " + crypto_currency + base_currency + " on bitbay and bittrex: ")
        while True:
            print(get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency,
                                                                         base_currency,
                                                                         "buy"))
            time.sleep(SLEEP_TIME)
    elif abc == "b":
        print("Difference for selling " + crypto_currency + base_currency + " on bitbay and bittrex: ")
        while True:
            get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency,
                                                                   "sell")
            time.sleep(SLEEP_TIME)
    elif abc == "c":
        print("Difference for buying " + crypto_currency + base_currency + " on bittrex and selling on bitbay: ")
        while True:
            get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency,
                                                                   "both")
            time.sleep(SLEEP_TIME)
    else:
        print(abc + " not in scope : {a,b,b}")


def exc_2(bitt_rex, bit_bay, crypto_currency, base_currency):
    print("EXC 2")
    print("Arbitrage while buying " + crypto_currency + base_currency + " on bittrex and selling on bitbay: ")
    while True:
        print(calculate_arbitrage(bitt_rex, bit_bay, crypto_currency, base_currency))
        time.sleep(SLEEP_TIME)


def calculate_arbitrage(bitt_rex, bit_bay, crypto_currency, base_currency):
    bitt_rex_order_book_json = bitt_rex.get_orderbook(crypto_currency, base_currency, "sell")
    bit_bay_order_book_json = bit_bay.get_transactions(crypto_currency, base_currency, "orderbook")
    bitt_rex_sell = bitt_rex_order_book_json['result']
    quick_sort_bitt_rex_by_rate(bitt_rex_sell)
    bitt_rex_best_sell = bitt_rex_sell[0]['Rate']
    bitt_rex_best_sell_amount = bitt_rex_sell[0]['Quantity']
    bit_bay_buy = bit_bay_order_book_json['bids']
    quick_sort_bit_bay_by_rate(bit_bay_buy)
    bit_bay_best_buy = bit_bay_buy[0][0]
    bit_bay_best_buy_amount = bit_bay_buy[0][1]

    if bit_bay_best_buy_amount < bitt_rex_best_sell_amount:  # if someone wants to buy less than i have to sell
        fees_for_bitt_rex = get_fees(bitt_rex, bitt_rex_best_sell, bit_bay_best_buy_amount, crypto_currency)
        fees_for_bit_bay = get_fees(bit_bay, bit_bay_best_buy, bit_bay_best_buy_amount, crypto_currency)
        return bit_bay_best_buy * bit_bay_best_buy_amount - bitt_rex_best_sell * bit_bay_best_buy_amount - fees_for_bitt_rex - fees_for_bit_bay
    else:
        missing_amount = bit_bay_best_buy_amount
        total = 0
        i = 0

        while missing_amount >= 0:
            fees_for_bitt_rex = get_fees(bitt_rex, bitt_rex_best_sell, bitt_rex_best_sell_amount, crypto_currency)
            fees_for_bit_bay = get_fees(bit_bay, bit_bay_best_buy, bitt_rex_best_sell_amount, crypto_currency)
            total = total + bit_bay_best_buy * bit_bay_best_buy_amount - bitt_rex_best_sell * bit_bay_best_buy_amount - fees_for_bitt_rex - fees_for_bit_bay
            missing_amount = missing_amount - bitt_rex_best_sell_amount
            i = i + 1
            bitt_rex_best_sell = bitt_rex_sell[i]['Rate']
            bitt_rex_best_sell_amount = bitt_rex_sell[i]['Quantity']

        return total


def get_fees(market, price, amount, crypto_currency):
    if crypto_currency in market.TRANSFER_FEE:
        return price * amount * market.TAKER_FEE + market.TRANSFER_FEE[crypto_currency]
    else:
        raise Exception("Transfer fee not mapped for " + crypto_currency)


def get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency, type):
    if type == "buy" or type == "sell" or type == "both":
        bitt_rex_order_book_json = bitt_rex.get_orderbook(crypto_currency, base_currency, type)
        bit_bay_order_book_json = bit_bay.get_transactions(crypto_currency, base_currency, "orderbook")
        if type == "buy" or type == "sell":
            bitt_rex_buy_sell = bitt_rex_order_book_json['result']
            quick_sort_bitt_rex_by_rate(bitt_rex_buy_sell)
            if type == "buy":
                bit_bay_buy = bit_bay_order_book_json['bids']
                quick_sort_bit_bay_by_rate(bit_bay_buy)
                bit_bay_best_buy = bit_bay_buy[len(bit_bay_buy) - 1][0]
                bitt_rex_best_sell = bitt_rex_buy_sell[len(bitt_rex_buy_sell) - 1]['Rate']
                return bit_bay_best_buy / bitt_rex_best_sell - 1
            else:
                bit_bay_buy = bit_bay_order_book_json['asks']
                quick_sort_bit_bay_by_rate(bit_bay_buy)
                bit_bay_best_sell = bit_bay_buy[0][0]
                bitt_rex_best_sell = bitt_rex_buy_sell[0]['Rate']
                return bit_bay_best_sell / bitt_rex_best_sell - 1
        else:
            bitt_rex_sell = bitt_rex_order_book_json['result']['sell']
            quick_sort_bitt_rex_by_rate(bitt_rex_sell)
            bitt_rex_best_sell = bitt_rex_sell[0]['Rate']
            bit_bay_buy = bit_bay_order_book_json['bids']
            quick_sort_bit_bay_by_rate(bit_bay_buy)
            bit_bay_best_buy = bit_bay_buy[0][0]
            return bit_bay_best_buy / bitt_rex_best_sell - 1
    else:
        print("Wrong type provided. Type has to be either buy, sell or both. Not: " + type)


def quick_sort_bit_bay_by_rate(unsorted):
    if len(unsorted) <= 1:
        return unsorted

    pivot = unsorted.pop()

    lower = []
    greater = []

    for item in unsorted:
        if item[0] < pivot[0]:
            lower.append(item)
        else:
            greater.append(item)

    return quick_sort_bit_bay_by_rate(lower) + [pivot] + quick_sort_bit_bay_by_rate(greater)


def quick_sort_bitt_rex_by_rate(unsorted):
    if len(unsorted) <= 1:
        return unsorted

    pivot = unsorted.pop()

    lower = []
    greater = []

    for item in unsorted:
        if item['Rate'] < pivot['Rate']:
            lower.append(item)
        else:
            greater.append(item)

    return quick_sort_bitt_rex_by_rate(lower) + [pivot] + quick_sort_bitt_rex_by_rate(greater)


bitt_rex = BittRexAPI()
bit_bay = BitBayAPI()
# exc_1(bitt_rex, bit_bay, CRYPTO_CURRENCY, BASE_CURRENCY, "a")
exc_2(bitt_rex, bit_bay, CRYPTO_CURRENCY, BASE_CURRENCY)
