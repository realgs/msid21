import time

from BittRexAPI import BittRexAPI

CURRENCY1_LIST = ["BTC", "LTC", "DASH"]
FIRST_CURRENCY = "BTC"
SECOND_CURRENCY = "LTC"
SLEEP_TIME = 5


def exc_1(bittRex, FIRST_CURRENCY, SECOND_CURRENCY):
    print("EXC 1")
    print("a")
    get_percentage_diff_for_best_buy_sell(bittRex, FIRST_CURRENCY, SECOND_CURRENCY, "buy")
    print("b")
    get_percentage_diff_for_best_buy_sell(bittRex, FIRST_CURRENCY, SECOND_CURRENCY, "sell")


def get_percentage_diff_for_best_buy_sell(bittRex, first_currency, second_currency, type):
    print(type)
    if type == "buy" or type == "sell":
        previousBest = -1
        while True:
            orderBookJSON = bittRex.get_orderbook(first_currency, second_currency, type)
            if type == "buy":
                allBuy = orderBookJSON['result']
                quick_sort_by_rate(allBuy)
                currentBest = allBuy[len(allBuy) - 1]['Rate']
            else:
                allSell = orderBookJSON['result']
                quick_sort_by_rate(allSell)
                currentBest = allSell[0]['Rate']

            if previousBest == -1: #first round
                previousBest = currentBest
            else:
                print(currentBest/previousBest - 1)
                previousBest = currentBest
            time.sleep(SLEEP_TIME)
    else:
        print("Wrong type provided. Type has to be either buy or sell. Not: " + type)


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


bittRex = BittRexAPI()
exc_1(bittRex, FIRST_CURRENCY, SECOND_CURRENCY)
