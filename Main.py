import time

from BittRexAPI import BittRexAPI

CURRENCY1_LIST = ["BTC", "LTC", "DASH"]
FIRST_CURRENCY = "BTC"
SECOND_CURRENCY = "LTC"
SLEEP_TIME = 5


def exc_1(bitt_rex, first_currency, second_currency):
    print("EXC 1")
    print("a")
    get_percentage_diff_for_best_buy_sell(bitt_rex, first_currency, second_currency, "buy")
    print("b")
    get_percentage_diff_for_best_buy_sell(bitt_rex, first_currency, second_currency, "sell")
    print("c")
    get_percentage_diff_for_best_buy_sell(bitt_rex, first_currency, second_currency, "both")


def get_percentage_diff_for_best_buy_sell(bitt_rex, first_currency, second_currency, type):
    if type == "buy" or type == "sell" or type == "both":
        previous_best = -1
        while True:
            order_book_json = bitt_rex.get_orderbook(first_currency, second_currency, type)
            if type == "buy" or type == "sell":
                all_buy_sell = order_book_json['result']
                quick_sort_by_rate(all_buy_sell)
                if type == "buy":
                    current_best = all_buy_sell[len(all_buy_sell) - 1]['Rate']
                else:
                    current_best = all_buy_sell[0]['Rate']
            else:
                all_buy = order_book_json['result']['buy']
                all_sell = order_book_json['result']['sell']
                quick_sort_by_rate(all_buy)
                quick_sort_by_rate(all_sell)
                best_buy = all_buy[len(all_buy) - 1]['Rate']
                best_sell = all_sell[0]['Rate']
                current_best = best_sell - best_buy

            if previous_best == -1:  # first round
                previous_best = current_best
            else:
                print(current_best / previous_best - 1)
                previous_best = current_best
            time.sleep(SLEEP_TIME)
    else:
        print("Wrong type provided. Type has to be either buy, sell or both. Not: " + type)


def quick_sort_by_rate(unsorted):
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

    return quick_sort_by_rate(lower) + [pivot] + quick_sort_by_rate(greater)


bitt_rex = BittRexAPI()
exc_1(bitt_rex, FIRST_CURRENCY, SECOND_CURRENCY)
