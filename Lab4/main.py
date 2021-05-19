from BitBayApi import BitBayApi
from BittrexApi import BittrexApi
from texttable import Texttable


def main():
    bitbay = BitBayApi()
    bittrex = BittrexApi()

    # Task 1.
    print("# TASK 1.")
    common_markets = find_common_markets(bitbay, bittrex)
    print_markets(common_markets)

    # Task 2.
    print("# TASK 2.")
    test_markets = {("ETH", "BTC"), ("LSK", "BTC"), ("TRX", "EUR")}
    arbitrages = calculate_arbitrages(bittrex, bitbay, test_markets)
    print_arbitrage_rating(arbitrages)

    # Task 3.
    print("# TASK 3.")
    arbitrages = calculate_arbitrages(bittrex, bitbay, common_markets)
    print_arbitrage_rating(arbitrages)


def find_common_markets(api1, api2):
    markets1 = api1.markets
    markets2 = api2.markets

    return markets1 & markets2


def print_markets(markets):
    markets = sorted(markets)

    for market in markets:
        print("{0}-{1}".format(market[0], market[1]))
    print()


def calculate_arbitrages(api1, api2, markets):
    arbitrages = set()

    for market in markets:
        arbitrages.add(calculate_arbitrage(api1, api2, market))

    return arbitrages


def calculate_arbitrage(api1, api2, market):
    asks = api1.getOrderbook(market)["asks"]
    bids = api2.getOrderbook(market)["bids"]

    volumes_to_trade = calculate_volumes_to_trade(asks, bids)

    asks = volumes_to_trade["asks"]
    bids = volumes_to_trade["bids"]

    asks_taker_fee = api1.fees["taker"]
    bids_taker_fee = api2.fees["taker"]

    purchase_cost = 0
    purchased_volume = 0

    for (volume, price) in asks:
        purchase_cost += price * volume
        purchased_volume += volume * (1 - asks_taker_fee)

    purchased_volume -= api1.fees["transfer"][market[1]]

    sale_profit = 0

    for (volume, price) in bids:
        if purchased_volume - volume <= 0:
            sale_profit += price * purchased_volume * (1 - bids_taker_fee)
            break

        purchased_volume -= volume
        sale_profit += price * volume * (1 - bids_taker_fee)

    difference = sale_profit - purchase_cost
    percent_difference = "{0:.2f}".format(difference / purchase_cost * 100)

    return market, difference, percent_difference


def calculate_volumes_to_trade(asks, bids):
    result = {"asks": [], "bids": []}

    if not asks or not bids:
        return result

    best_ask = asks[0]
    best_bid = bids[0]

    if best_ask[1] >= best_bid[1]:
        max_volume = min(best_ask[0], best_bid[0])
        result["asks"].append((max_volume, best_ask[1]))
        result["bids"].append((max_volume, best_bid[1]))

        return result

    for i in range(len(asks) - 1, -1, -1):
        ask = asks[i]
        if ask[1] < best_bid[1]:
            bids_temp = []

            for bid in bids:
                if ask[1] < bid[1]:
                    bids_temp.append(bid)
                else:
                    break
            bids = bids_temp
            asks = asks[:i + 1]
            break

    bids_volume = 0
    asks_volume = 0

    for bid in bids:
        bids_volume += bid[0]

    for ask in asks:
        asks_volume += ask[0]

    max_volume = min(bids_volume, asks_volume)

    bids_volume = 0
    asks_volume = 0

    for bid in bids:
        if bids_volume + bid[0] >= max_volume:
            result["bids"].append((max_volume - bids_volume, bid[1]))
            break

        bids_volume += bid[0]
        result["bids"].append(bid)

    for ask in asks:
        if asks_volume + ask[0] >= max_volume:
            result["asks"].append((max_volume - asks_volume, ask[1]))
            break

        asks_volume += ask[0]
        result["asks"].append(ask)

    return result


def print_arbitrage_rating(arbitrages):
    differences_table = create_table(["MARKET", "CURRENCY DIFFERENCE", "% DIFFERENCE"], ["l", "r", "r"],
                                     ["t", "f", "f"], ["l", "r", "r"])

    for arbitrage in sorted(arbitrages, key=lambda x: float(x[2]), reverse=True):
        market, currency_difference, percent_difference = arbitrage
        differences_table.add_row(
            ["{0}-{1}".format(market[0], market[1]), "{0:.8f} {1}".format(currency_difference, market[0]),
             percent_difference])
    print("\n", differences_table.draw())
    print()


def create_table(header, header_align, cols_dtype, cols_align, precision=2, deco=Texttable.HEADER):
    table = Texttable()
    table.header(header)
    table.set_header_align(header_align)
    table.set_cols_dtype(cols_dtype)
    table.set_cols_align(cols_align)
    table.set_precision(precision)
    table.set_deco(deco)
    return table


if __name__ == '__main__':
    main()
