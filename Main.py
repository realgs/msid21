import time

from BitBayAPI import BitBayAPI
from BittRexAPI import BittRexAPI

CRYPTO_CURRENCY = "BTC"
BASE_CURRENCY = "USD"
SLEEP_TIME = 5


def exc_1(bitt_rex, bit_bay, crypto_currency, base_currency):
    print("EXC 1")
    print("a")
    print("Difference for buying " + crypto_currency + base_currency + " on bitbay and bittrex: ")
    while True:
        print(get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency,
                                                                     "buy"))
        time.sleep(SLEEP_TIME)
    print("b")
    print("Difference for selling " + crypto_currency + base_currency + " on bitbay and bittrex: ")
    while True:
        get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency, "sell")
        time.sleep(SLEEP_TIME)
    print("c")
    print("Difference for buying " + crypto_currency + base_currency + " on bittrex and selling on bitbay: ")
    while True:
        get_percentage_diff_for_best_buy_sell_on_diff_stock_ex(bitt_rex, bit_bay, crypto_currency, base_currency, "both")
        time.sleep(SLEEP_TIME)


def exc_2(bitt_rex, bit_bay, crypto_currency, base_currency):
    print("EXC 2")
    while True:
        calculate_arbitrage(bitt_rex, bit_bay, crypto_currency, base_currency)
        time.sleep(SLEEP_TIME)


def calculate_arbitrage(bitt_rex, bit_bay, crypto_currency, base_currency):
    pass


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
                bitt_rex_best_buy = bitt_rex_buy_sell[len(bitt_rex_buy_sell) - 1]['Rate']
                return bit_bay_best_buy / bitt_rex_best_buy - 1
            else:
                bit_bay_sell = bit_bay_order_book_json['asks']
                quick_sort_bit_bay_by_rate(bit_bay_sell)
                bit_bay_best_sell = bit_bay_sell[0][0]
                bitt_rex_best_sell = bitt_rex_buy_sell[0]['Rate']
                return bit_bay_best_sell / bitt_rex_best_sell - 1
        else:
            bitt_rex_buy = bitt_rex_order_book_json['result']['buy']
            quick_sort_bitt_rex_by_rate(bitt_rex_buy)
            bitt_rex_best_buy = bitt_rex_buy[len(bitt_rex_buy) - 1]['Rate']
            bit_bay_sell = bit_bay_order_book_json['asks']
            quick_sort_bit_bay_by_rate(bit_bay_sell)
            bit_bay_best_sell = bit_bay_sell[0][0]
            return bitt_rex_best_buy / bit_bay_best_sell - 1
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
exc_1(bitt_rex, bit_bay, CRYPTO_CURRENCY, BASE_CURRENCY)
