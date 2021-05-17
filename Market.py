import time

from MarketFunctions import load_data
from MarketFormatTransformer import MarketFormatTransformer
from MarketConstants import ARBITRATION_MINIMUM


class Market:
    def __init__(self, market_name, url, currencies, withdrawal_fees, taker_fee):
        self.__market_name = market_name
        self.__currencies = currencies
        self.__bid_offers, self.__ask_offers = Market.__get_offers(market_name, url, currencies)
        self.__withdrawal_fees = withdrawal_fees
        self.__taker_fee = taker_fee

    @staticmethod
    def __get_offers(market_name, url, currencies):
        bid_ask_offers = []

        for currency in currencies:
            base_index = 0 if market_name != "poloniex" else 1
            quote_index = 1 if market_name != "poloniex" else 0

            base_currency = currency[base_index]
            quote_currency = currency[quote_index]
            offers_for_currencies = load_data(url.format(base_currency, quote_currency))
            bid_ask_offers.append(offers_for_currencies)
            time.sleep(0.1)

        return MarketFormatTransformer.transform_market_format(market_name, bid_ask_offers)

    def get_arbitration_result(self, sell_market):
        arbitration_result = []

        for i in range(len(self.__currencies)):
            base_index = 0
            quote_index = 1

            base_currency = self.__currencies[i][base_index]
            quote_currency = self.__currencies[i][quote_index]

            withdrawal_fee = float(self.__withdrawal_fees[base_currency])

            arbitration_gain = Market.__count_arbitration_result(self.__ask_offers[i], sell_market.__bid_offers[i],
                                                                 self.__taker_fee,
                                                                 sell_market.__taker_fee, withdrawal_fee)
            arbitration_result.append(("{}->{}".format(self.__market_name, sell_market.__market_name),
                                       "{}-{}".format(base_currency, quote_currency),
                                       arbitration_gain))

        return arbitration_result

    @staticmethod
    def __count_arbitration_result(ask_offers, bid_offers, taker_ask_fee, taker_bid_fee, withdrawal_fee):
        arbitration_best_result = (0, 0, ARBITRATION_MINIMUM)

        for i in range(len(ask_offers)):
            for j in range(len(bid_offers)):
                current_ask_offers = ask_offers[:i+1]
                current_bid_offers = bid_offers[:j+1]
                expense, gain, volume = Market.__get_best_current_arbitration(current_ask_offers, current_bid_offers,
                                                                              taker_ask_fee, taker_bid_fee,
                                                                              withdrawal_fee)
                percent_gain = (gain - expense) / expense
                if percent_gain > arbitration_best_result[2]:
                    arbitration_best_result = (gain - expense, volume, percent_gain)

        return arbitration_best_result

    @staticmethod
    def __get_best_current_arbitration(ask_offers, bid_offers, taker_ask_fee, taker_bid_fee, withdrawal_fee):
        ask_offers_volume = sum(offer[1] for offer in ask_offers)
        bid_offers_volume = sum(offer[1] for offer in bid_offers)

        volume = min(ask_offers_volume, bid_offers_volume)
        expense = 0
        gain = 0

        ask_volume = volume
        bid_volume = max(volume - withdrawal_fee, 0)

        for offer in bid_offers:
            if bid_volume < offer[1]:
                gain += bid_volume * offer[0]
                break
            gain += offer[1] * offer[0]
            bid_volume -= offer[1]

        for offer in ask_offers:
            if ask_volume < offer[1]:
                expense += ask_volume * offer[0]
                break
            expense += offer[1] * offer[0]
            ask_volume -= offer[1]

        expense *= (1 + taker_ask_fee)
        gain *= (1 - taker_bid_fee)

        return expense, gain, volume
