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
    bitbay = BitBayApi()
    bittrex = BittrexApi()

    # Task 1.
    common_markets = find_common_markets(bitbay, bittrex)
    print_markets(common_markets)

    # Task 2.
    test_markets = {("ETH", "BTC"), ("LSK", "BTC"), ("LTC", "USD")}
    arbitrages = calculate_arbitrages(bitbay, bittrex, test_markets)
    print_arbitrage_rating(arbitrages)

    # Task 3.
    arbitrages = calculate_arbitrages(bitbay, bittrex, common_markets)
    print_arbitrage_rating(arbitrages)


def calculate_arbitrages(api1, api2, markets):
    arbitrages = set()

    for market in markets:
        arbitrages.add(calculate_arbitrage(api1, api2, market))

    return arbitrages


def calculate_arbitrage(api1, api2, market):
    pass


def print_arbitrage_rating(arbitrages):
    pass


if __name__ == '__main__':
    main()
