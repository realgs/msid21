import time

from Finance_l4 import bitbay, bittrex
from Finance_l4.apiCompare import getMarketsIntersection, getBuySellInfo, printArbitrageInfo

REFRESH = 5


def main():
    while True:
        # task1
        bitbay_list = bitbay.createMarketsList()
        bittrex_list = bittrex.createMarketsList()
        markets_intersection = getMarketsIntersection(bitbay_list, bittrex_list)
        print(markets_intersection)

        # task2 [GRT-USDT, LTC-USD, BSV-EUR]
        currencies = []
        for curr in markets_intersection:
            currencies.append(curr.split('-'))

        sell_buy_info_1 = getBuySellInfo(currencies[0][0], currencies[0][1])
        sell_buy_info_2 = getBuySellInfo(currencies[1][0], currencies[1][1])
        sell_buy_info_3 = getBuySellInfo(currencies[2][0], currencies[2][1])

        printArbitrageInfo(sell_buy_info_1, currencies[0][0], currencies[0][1])
        printArbitrageInfo(sell_buy_info_2, currencies[1][0], currencies[1][1])
        printArbitrageInfo(sell_buy_info_3, currencies[2][0], currencies[2][1])
        time.sleep(REFRESH)


if __name__ == "__main__":
    main()
