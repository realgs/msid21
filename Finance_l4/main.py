import time

from Finance_l4 import bitbay, bittrex
from Finance_l4.apiCompare import getMarketsIntersection, getBuySellInfo, printArbitrageInfo, getArbitrageInfo

REFRESH = 5
RANKING = "\nRanking: "


def main():
    while True:

        # task1
        bitbay_list = bitbay.createMarketsList()
        bittrex_list = bittrex.createMarketsList()
        markets_intersection = getMarketsIntersection(bitbay_list, bittrex_list)
        print(markets_intersection)

        # task2
        currencies = []
        for currency in markets_intersection:
            currencies.append(currency.split('-'))

        sell_buy_info_1 = getBuySellInfo(currencies[0][0], currencies[0][1])
        sell_buy_info_2 = getBuySellInfo(currencies[1][0], currencies[1][1])
        sell_buy_info_3 = getBuySellInfo(currencies[2][0], currencies[2][1])

        printArbitrageInfo(getArbitrageInfo(sell_buy_info_1, currencies[0][0], currencies[0][1]))
        printArbitrageInfo(getArbitrageInfo(sell_buy_info_2, currencies[1][0], currencies[1][1]))
        printArbitrageInfo(getArbitrageInfo(sell_buy_info_3, currencies[2][0], currencies[2][1]))

        # task 3
        results_ranking = []
        for currency in currencies:
            sell_buy_info = getBuySellInfo(currency[0], currency[1])
            result = getArbitrageInfo(sell_buy_info, currencies[0][0], currencies[0][1])
            results_ranking.append(result[0])
            results_ranking.append(result[1])

        results_ranking.sort(key=lambda result: result[3], reverse=True)
        print(RANKING)
        for value in results_ranking:
            print(value)
        time.sleep(REFRESH)


if __name__ == "__main__":
    main()
