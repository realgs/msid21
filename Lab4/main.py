from BitBayApi import BitBayApi
from BittrexApi import BittrexApi


def find_common_markets(api1, api2):
    markets1 = api1.markets
    markets2 = api2.markets

    return markets1 & markets2


def print_markets(markets):
    markets = sorted(markets)

    for market in markets:
        print("{0}-{1}".format(market[0], market[1]))


def main():
    bba = BitBayApi()
    bitrxa = BittrexApi()

    # Task 1.
    common_markets = find_common_markets(bba, bitrxa)
    print_markets(common_markets)


if __name__ == '__main__':
    main()
