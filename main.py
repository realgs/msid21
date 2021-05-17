from Market import Market
from MarketConstants import *
from MarketFunctions import find_common_markets, withdrawal_fees_poloniex, withdrawal_fees_bittrex,\
    print_arbitration_result, currency_to_usd


def main():
    common_markets = find_common_markets()

    market1 = Market(MARKET_POLONIEX["name"], MARKET_POLONIEX["url"], common_markets,
                     withdrawal_fees_poloniex(), MARKET_POLONIEX["taker_fee"])
    market2 = Market(MARKET_BITTREX["name"], MARKET_BITTREX["url"], common_markets,
                     withdrawal_fees_bittrex(), MARKET_BITTREX["taker_fee"])

    arbitration = market2.get_arbitration_result(market1) + market1.get_arbitration_result(market2)

    for i in range(len(arbitration)):
        currency = arbitration[i][1].split("-")[1]
        amount_of_currency = currency_to_usd(arbitration[i][2][0], currency)

        arbitration[i] = (arbitration[i][0], arbitration[i][1], amount_of_currency, arbitration[i][2][1],
                          arbitration[i][2][2])

    arbitration.sort(key=lambda x: x[4], reverse=True)
    print_arbitration_result(arbitration)


if __name__ == '__main__':
    main()
