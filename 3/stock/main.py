import time
from stock.data_parser import DataParser
from stock.utils import *

NUMBER_OF_OFFERS = 10


class Main:

    @staticmethod
    def exercise_3():
        while True:
            Main.compare("GBP", "LTC", "asks")
            Main.compare("EUR", "BTC", "bids")
            Main.kraken_bitbay_ideal_arbitrage("USD", "BTC")
            Main.bitbay_kraken_ideal_arbitrage("EUR", "DASH")
            print()
            time.sleep(5)

    @staticmethod
    def exercise_4():
        while True:
            Main.kraken_bitbay_arbitrage("USD", "BTC")
            print()
            Main.bitbay_kraken_arbitrage("EUR", "LTC")
            print()
            time.sleep(5)

    @staticmethod
    def kraken_bitbay_arbitrage(currency, cryptocurrency):
        data_parser = DataParser(currency, cryptocurrency)
        kraken_trades = data_parser.kraken_withdraw("asks", currency)
        bitbay_trades = data_parser.bitbay_deposit("bids", currency)
        result = Main.trade_stocks(kraken_trades, bitbay_trades)
        print("{0} {1} are available for Kraken - Bitbay {2}{1} arbitrage.".format(round(result[0], 2), currency, cryptocurrency))
        print("{0}% can be earned for a total of {1} {2}.".format(round(result[1], 2), round(result[2], 2), currency))

    @staticmethod
    def bitbay_kraken_arbitrage(currency, cryptocurrency):
        data_parser = DataParser(currency, cryptocurrency)
        kraken_trades = data_parser.kraken_deposit("bids", currency)
        bitbay_trades = data_parser.bitbay_withdraw("asks", currency)
        result = Main.trade_stocks(bitbay_trades, kraken_trades)
        print("{0} {1} are available for Bitbay - Kraken {2}{1} arbitrage.".format(round(result[0], 2), currency, cryptocurrency))
        print("{0}% can be earned for a total of {1} {2}.".format(round(result[1], 2), round(result[2], 2), currency))

    @staticmethod
    def trade_stocks(to_purchase, to_sell):
        money_spend = 0
        money_earned = 0
        for buy_trade in to_purchase:
            for sell_trade in to_sell:
                buy_exchange_rate = get_exchange_rate(buy_trade)
                sell_exchange_rate = get_exchange_rate(sell_trade)
                if buy_exchange_rate < sell_exchange_rate:
                    stocks_bought = min(buy_trade[1], sell_trade[1])
                    money_spend += buy_exchange_rate * stocks_bought
                    money_earned += sell_exchange_rate * stocks_bought
                    buy_trade[0] -= buy_exchange_rate * stocks_bought
                    buy_trade[1] -= stocks_bought
                    sell_trade[0] -= sell_exchange_rate * stocks_bought
                    sell_trade[1] -= stocks_bought
                    if sell_trade[1] == 0:
                        to_sell.remove(sell_trade)
                    if buy_trade[1] == 0:
                        to_purchase.remove(buy_trade)
                        break
        profit = money_earned - money_spend
        percentage_earned = profit / money_spend * 100 if money_spend != 0 else 0
        return money_spend, percentage_earned, profit

    @staticmethod
    def kraken_bitbay_ideal_arbitrage(currency, cryptocurrency):
        data_parser = DataParser(currency, cryptocurrency)

        bitbay_data = data_parser.bitbay_trades('bids')
        kraken_data = data_parser.kraken_trades('asks')
        kraken_buy = Main.lowest(kraken_data)
        bitbay_sell = Main.highest(bitbay_data)

        percentage_difference = 100 * ((bitbay_sell - kraken_buy) / bitbay_sell)

        if percentage_difference > 0:
            print(
                'Kraken - Bitbay {0} Arbitrage is profitable with a profit of {1} %.'.format(cryptocurrency + currency,
                                                                                             round(
                                                                                                 percentage_difference,
                                                                                                 2)))
        else:
            print('Kraken - Bitbay {0} Arbitrage is not profitable with a loss of {1} %.'.format(
                cryptocurrency + currency, round(-percentage_difference, 2)))

    @staticmethod
    def bitbay_kraken_ideal_arbitrage(currency, cryptocurrency):
        data_parser = DataParser(currency, cryptocurrency)

        bitbay_data = data_parser.bitbay_trades('asks')
        kraken_data = data_parser.kraken_trades('bids')
        kraken_sell = Main.highest(kraken_data)
        bitbay_buy = Main.lowest(bitbay_data)

        percentage_difference = 100 * ((kraken_sell - bitbay_buy) / kraken_sell)

        if percentage_difference > 0:
            print(
                'Kraken - Bitbay {0} Arbitrage is profitable with a profit of {1} %.'.format(cryptocurrency + currency,
                                                                                             round(
                                                                                                 percentage_difference,
                                                                                                 2)))
        else:
            print('Kraken - Bitbay {0} Arbitrage is not profitable with a loss of {1} %.'.format(
                cryptocurrency + currency, round(-percentage_difference, 2)))

    @staticmethod
    def compare(currency, cryptocurrency, key):
        data_parser = DataParser(currency, cryptocurrency)

        bitbay_data = data_parser.bitbay_trades(key)
        kraken_data = data_parser.kraken_trades(key)
        bitbay_avg = Main.average(bitbay_data)
        kraken_avg = Main.average(kraken_data)
        if bitbay_avg > kraken_avg:
            exchange_rate_difference = ((bitbay_avg - kraken_avg) / bitbay_avg) * 100
            print('Bitbay {0} are {1} % more expensive than Kraken {0} for {2}.'.format(key,
                                                                                        round(exchange_rate_difference,
                                                                                              2),
                                                                                        cryptocurrency + currency))
        else:
            exchange_rate_difference = ((kraken_avg - bitbay_avg) / kraken_avg) * 100
            print('Kraken {0} are {1} % more expensive than Bitbay {0} for {2}.'.format(key,
                                                                                        round(exchange_rate_difference,
                                                                                              2),
                                                                                        cryptocurrency + currency))

    @staticmethod
    def average(data):
        avg = 0
        for entry in data:
            avg += get_exchange_rate(entry)
        avg /= len(data)
        return avg

    @staticmethod
    def highest(data):
        highest = -1
        for entry in data:
            exchange_rate = get_exchange_rate(entry)
            if exchange_rate > highest:
                highest = exchange_rate
        return highest

    @staticmethod
    def lowest(data):
        lowest = 1000000
        for entry in data:
            exchange_rate = get_exchange_rate(entry)
            if exchange_rate < lowest:
                lowest = exchange_rate
        return lowest


if __name__ == '__main__':
    Main.exercise_4()
