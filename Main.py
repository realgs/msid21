import random

import time

from BitBayAPI import BitBayAPI
from BittRexAPI import BittRexAPI

CRYPTO_CURRENCY = "BTC"
BASE_CURRENCY = "USD"
SLEEP_TIME = 5


# W sposób automatyczny znaleźć wspólny zbiór par walutowych oferowanych przez dwie analizowane giełdy.
def find_common_markets(bitt_rex, bit_bay):
    all_markets_bitt_rex = bitt_rex.get_market_names_list()
    all_markets_bit_bay = bit_bay.get_market_names_list()
    common_markets = get_common_elements_in_two_lists(all_markets_bitt_rex, all_markets_bit_bay)
    return common_markets


def get_common_elements_in_two_lists(list1, list2):
    list1_as_set = set(list1)
    return list(list1_as_set.intersection(list2))


# Wykorzystując rozwiązanie szukające możliwości arbitrażu z listy poprzedniej (z uwzględnieniem opłat i wolumenów) sprawdzić możliwość wykonania arbitrażu na dowolnych trzech zasobach ze zbioru uzyskanego w zadaniu 1.
# Upewnić się, że Wasze rozwiązanie szuka wgłąb rynku, a nie jedynie wśród pierwszych (najlepszych) ofert. Dla każdej pary walutowej zwrócić informację o potencjalnej wielkości zysku lub jego braku.
def get_arbitrage_on_three_resources(bitt_rex, bit_bay):
    common_markets = find_common_markets(bitt_rex, bit_bay)
    three_common_markets = []
    while len(three_common_markets) <= 3:
        random_index = random.randint(0, len(common_markets) - 1)
        three_common_markets.append(common_markets[random_index])

    while True:
        for market in three_common_markets:
            currency_pair = market.split("-")
            print("Arbitrage while buying " + market + " on bittrex and selling on bitbay: ")
            print(calculate_arbitrage(bitt_rex, bit_bay, currency_pair[0], currency_pair[1]))
        time.sleep(SLEEP_TIME)


def rank_arbitrage_for_all_markets(bitt_rex, bit_bay):
    common_markets = find_common_markets(bitt_rex, bit_bay)
    arbitrage_map = {}
    for market in common_markets:
        current_pair = market.split("-")
        arbitrage = calculate_arbitrage(bitt_rex, bit_bay, current_pair[0], current_pair[1])
        if arbitrage is not None:
            arbitrage_map[market] = arbitrage

    sorted_arbitrage_map = sorted(arbitrage_map.items(), key=lambda x: x[1], reverse=True)
    print("Arbitrage rank:")
    print(sorted_arbitrage_map)


def calculate_arbitrage(bitt_rex, bit_bay, crypto_currency, base_currency):
    bitt_rex_order_book_json = bitt_rex.get_orderbook(crypto_currency, base_currency, "sell")
    bit_bay_order_book_json = bit_bay.get_orderbook(crypto_currency, base_currency, "buy")
    bitt_rex_sell = bitt_rex_order_book_json['result']
    bit_bay_buy = bit_bay_order_book_json
    if len(bitt_rex_sell) == 0 or len(bit_bay_buy) == 0:
        print("No offer was found for " + crypto_currency + "-" + base_currency + " on ", "bit_rex" if len(bitt_rex_sell) == 0 else "bit_bay")
    else:
        quick_sort_by_rate(bitt_rex_sell, 'Rate')
        bitt_rex_best_sell = bitt_rex_sell[0]['Rate']
        bitt_rex_best_sell_amount = bitt_rex_sell[0]['Quantity']
        quick_sort_by_rate(bit_bay_buy, 'ra')
        bit_bay_best_buy = float(bit_bay_buy[0]['ra'])
        bit_bay_best_buy_amount = float(bit_bay_buy[0]['ca'])

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


def quick_sort_by_rate(unsorted, rate_key):
    if len(unsorted) <= 1:
        return unsorted

    pivot = unsorted.pop()

    lower = []
    greater = []

    for item in unsorted:
        if item.get(rate_key) < pivot.get(rate_key):
            lower.append(item)
        else:
            greater.append(item)

    return quick_sort_by_rate(lower, rate_key) + [pivot] + quick_sort_by_rate(greater, rate_key)


bitt_rex = BittRexAPI()
bit_bay = BitBayAPI()
# find_common_markets(bitt_rex, bit_bay)
# get_arbitrage_on_three_resources(bitt_rex, bit_bay)
rank_arbitrage_for_all_markets(bitt_rex, bit_bay)
# calculate_arbitrage(bitt_rex, bit_bay, "NPXS", "BTC")
