from data_parser import *
from fees_provider import *
import random


class Main:
    fees_provider = FeesProvider()
    common_markets = DataParser.common_markets()
    bittrex_fee = 0.2
    poloniex_fee = 0.125

    @staticmethod
    def rank_arbitrages():
        results = []

        for base in Main.common_markets:
            for target in Main.common_markets[base]:
                results.append(("Bittrex-Poloniex", base, target, Main.bittrex_poloniex_arbitrage(target, base)))
                results.append(("Poloniex-Bittrex", base, target, Main.poloniex_bittrex_arbitrage(target, base)))

        results = sorted(results, key=lambda result: result[3][0] / result[3][1] if result[3][1] != 0 else 0,
                         reverse=True)

        for i in range(0, len(results)):
            print("{0}. {1} {2}{3} arbitrage: {4} {3} can be traded for a {5}({6} %){3} gain.".format(i + 1, results[i][0],
                results[i][2], results[i][1], results[i][3][1], results[i][3][0], results[i][3][0] / (results[i][3][1] / 100) if results[i][3][1] != 0 else 0))

    @staticmethod
    def three_arbitrages():
        for _ in range(0, 3):
            pair = Main.random_pair()
            bp_result = Main.bittrex_poloniex_arbitrage(pair[1], pair[0])
            pb_result = Main.poloniex_bittrex_arbitrage(pair[1], pair[0])
            print(bp_result)
            print(pb_result)

            print("{0} {1} are available for Bittrex-Poloniex {2}{1} arbitrage.".format(bp_result[1], pair[0],
                                                                                        pair[1]))
            print("{0} % can be earned for a total of {1} {2}.".format(
                bp_result[0] / (bp_result[1] / 100) if bp_result[1] != 0 else 0, bp_result[0], pair[0]))

            print("{0} {1} are available for Poloniex-Bittrex {2}{1} arbitrage.".format(pb_result[1], pair[0], pair[1]))

            print("{0} % can be earned for a total of {1} {2}.".format(
                pb_result[0] / (pb_result[1] / 100) if pb_result[1] != 0 else 0, pb_result[0], pair[0]))

    @staticmethod
    def bittrex_poloniex_arbitrage(target, base):
        bittrex_bids = FeesProvider.trades_after_fee(DataParser.bittrex_offers(base, target, "buy"), Main.bittrex_fee,
                                                     "bids")
        poloniex_asks = FeesProvider.trades_after_fee(DataParser.poloniex_offers(base, target, "asks"),
                                                      Main.poloniex_fee,
                                                      "asks")
        bittrex_bids = Main.sorted_by_exchange_rate(bittrex_bids, True)
        poloniex_asks = Main.sorted_by_exchange_rate(poloniex_asks, False)

        result = Main.trade_stocks(bittrex_bids, poloniex_asks, Main.fees_provider.bittrex_withdrawal_fee(target))

        return result

    @staticmethod
    def poloniex_bittrex_arbitrage(target, base):
        poloniex_bids = FeesProvider.trades_after_fee(DataParser.poloniex_offers(base, target, "bids"),
                                                      Main.poloniex_fee,
                                                      "bids")
        bittrex_asks = FeesProvider.trades_after_fee(DataParser.bittrex_offers(base, target, "sell"), Main.bittrex_fee,
                                                     "asks")
        poloniex_bids = Main.sorted_by_exchange_rate(poloniex_bids, True)
        bittrex_asks = Main.sorted_by_exchange_rate(bittrex_asks, False)

        result = Main.trade_stocks(poloniex_bids, bittrex_asks, Main.fees_provider.poloniex_withdrawal_fee(target))

        return result

    @staticmethod
    def trade_stocks(bids, asks, withdrawal_fee):
        possible_buys = [Main.buy_all(bids[0:i], withdrawal_fee) for i in range(0, len(bids))]
        possible_sells = [asks[0:i] for i in range(0, len(asks))]
        results = []

        for possible_buy in possible_buys:
            for possible_sell in possible_sells:
                results.append((possible_buy[0], Main.sell_all(possible_sell, possible_buy[1])))

        result = max(results, key=lambda r: r[1] - r[0]) if len(results) != 0 else (0, 0)

        return result

    @staticmethod
    def buy_all(bids, withdrawal_fee):
        quantity_bought = sum(bid[0] for bid in bids) - withdrawal_fee
        currency_spent = sum(bid[0] * bid[1] for bid in bids)

        return currency_spent, quantity_bought

    @staticmethod
    def sell_all(asks, quantity):
        currency_earned = 0

        for i in range(0, len(asks)):
            quantity_sold = min(quantity, asks[i][1])
            quantity -= quantity_sold
            asks[i][1] -= quantity_sold
            currency_earned += quantity_sold * asks[i][0]

            if quantity == 0:
                break

        return currency_earned

    @staticmethod
    def random_pair():
        base = random.choice(list(Main.common_markets))

        return base, random.choice(list(Main.common_markets[base]))

    @staticmethod
    def sorted_by_exchange_rate(trades, descending):
        return sorted(trades, key=lambda trade: trade[0], reverse=descending)


if __name__ == '__main__':
    Main.rank_arbitrages()
