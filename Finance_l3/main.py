import time

from Finance_l3.calculations import printDifferences, printArbitrageInfo, getBuySellInfo, printSellBuyInfo

REFRESH = 5


def main():
    while True:
        # task1
        buy_sell_info = getBuySellInfo()
        printSellBuyInfo(buy_sell_info)
        printDifferences(buy_sell_info)
        # task2
        printArbitrageInfo(buy_sell_info)
        time.sleep(REFRESH)


if __name__ == "__main__":
    main()
