from stock_exchange.utils import *
import re


class ArbitrageChecker:
    def __init__(self):
        self._bittrex_withdrawal_fees = {}
        bittrex_response = connect("{}/getcurrencies".format(bittrex))

        for entry in bittrex_response["result"]:
            self._bittrex_withdrawal_fees[entry["Currency"]] = entry["TxFee"]

        self._bitbay_withdrawal_fees = {}

        for line in open("bitbay_withdrawal.txt").readlines():
                splitted = re.split("\\s+", line)
                self._bitbay_withdrawal_fees[splitted[0]] = splitted[1]

    def _bittrex_withdrawal_fee(self, currency):
        return float(self._bittrex_withdrawal_fees[currency])

    def _bitbay_withdrawal_fee(self, currency):
        return float(self._bitbay_withdrawal_fees[currency])

    def bittrex_bitbay_arbitrage(self, base, target, quantity):
        bittrex_bids = self._bittrex_offers(base, target, "buy")
        bitbay_asks = self._bitbay_offers(base, target, "sell")

        bittrex_bids = ArbitrageChecker._sorted_by_exchange_rate(bittrex_bids, True)
        bitbay_asks = ArbitrageChecker._sorted_by_exchange_rate(bitbay_asks, False)

        return ArbitrageChecker._trade_stocks(bittrex_bids, bitbay_asks, quantity)

    def bitbay_bittrex_arbitrage(self, base, target, quantity):
        bitbay_bids = self._bitbay_offers(base, target, "buy")
        bittrex_asks = self._bittrex_offers(base, target, "sell")

        bitbay_bids = ArbitrageChecker._sorted_by_exchange_rate(bitbay_bids, True)
        bittrex_asks = ArbitrageChecker._sorted_by_exchange_rate(bittrex_asks, False)

        return ArbitrageChecker._trade_stocks(bitbay_bids, bittrex_asks, quantity)

    def _bittrex_offers(self, base, target, type):
        response = connect("{}getorderbook?market={}-{}&type={}".format(bittrex, base, target, type))
        offers = []

        if response["message"] == 'INVALID_MARKET':
            return offers

        for offer in response['result']:
            rate = float(offer['Rate'])
            if type == 'buy':
                rate = rate * (1 + bitbay_fee / 100)
            else:
                rate = rate * (1 - bittrex_fee / 100)

            quantity = float(offer['Quantity'])

            if type == 'buy':
                quantity -= self._bitbay_withdrawal_fee(target)

            offers.append((rate, quantity))

        return offers

    def _bitbay_offers(self, base, target, type):
        response = connect("{}orderbook/{}-{}".format(bitbay, target, base))
        offers = []

        if response['status'] == 'Fail':
            return offers

        for offer in response[type]:
            rate = float(offer['ra'])
            if type == 'buy':
                rate = rate * (1 + bitbay_fee / 100)
            else:
                rate = rate * (1 - bittrex_fee / 100)

            quantity = float(offer['ca'])

            if type == 'buy':
                quantity -= self._bitbay_withdrawal_fee(target)

            offers.append((rate, quantity))

        return offers

    @staticmethod
    def _trade_stocks(bids, asks, quantity):
        possible_buys = []

        for i in range (0, len(bids)):
            trade = ArbitrageChecker._buy_all(bids[:i])
            current_quantity = trade[1]

            if current_quantity > quantity:
                break

            possible_buys.append(trade)

        possible_sells = [asks[0:i] for i in range(0, len(asks))]
        results = []

        for possible_buy in possible_buys:
            for possible_sell in possible_sells:
                results.append((possible_buy[0], ArbitrageChecker._sell_all(possible_sell, possible_buy[1])))

        result = max(results, key=lambda r: r[1] - r[0]) if len(results) != 0 else (0, 0)

        return result

    @staticmethod
    def _buy_all(bids):
        quantity_bought = sum(bid[0] for bid in bids)
        currency_spent = sum(bid[0] * bid[1] for bid in bids)

        return currency_spent, quantity_bought

    @staticmethod
    def _sell_all(asks, quantity):
        currency_earned = 0

        for i in range(0, len(asks)):
            quantity_sold = min(quantity, asks[i][1])
            quantity -= quantity_sold
            asks[i] = (asks[i][0], asks[i][1] - quantity_sold)
            currency_earned += quantity_sold * asks[i][0]

            if quantity == 0:
                break

        return currency_earned

    @staticmethod
    def _sorted_by_exchange_rate(trades, descending):
        return sorted(trades, key=lambda trade: trade[0], reverse=descending)
