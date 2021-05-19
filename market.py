import requests
import constants_binance
import constants_bitbay
import Bitbay
import Binance


class Market:
    def __init__(self, name, pairs):
        self.name = name
        self.pairs = pairs

    def get_orderbook(self, pair):
        result = None
        if self.name == constants_bitbay.NAME:
            result = Bitbay.get_orderbook(pair, 50)
        elif self.name == constants_binance.NAME:
            result = Binance.get_orderbook(pair, 50)
        return result

    def get_pairs(self):
        result = None
        if self.name == constants_bitbay.NAME:
            result = constants_bitbay.PAIRS
        elif self.name == constants_binance.NAME:
            result = constants_binance.PAIRS
        return result

    def get_taker_fee(self):
        result = None
        if self.name == constants_bitbay.NAME:
            result = constants_bitbay.TAKER_FEE
        elif self.name == constants_binance.NAME:
            result = constants_binance.TAKER_FEE
        return result

    def get_order(self):
        result = None
        if self.name == constants_bitbay.NAME:
            result = constants_bitbay.ORDER
        elif self.name == constants_binance.NAME:
            result = constants_binance.ORDER
        return result

    def get_withdrawal_fees(self):
        result = None
        if self.name == constants_bitbay.NAME:
            result = constants_bitbay.WITHDRAWAL_FEES
        elif self.name == constants_binance.NAME:
            result = constants_binance.WITHDRAWAL_FEES
        return result
