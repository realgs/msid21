import re
import math


class FeesProvider:

    @staticmethod
    def read_fees(filepath):
        text_file = open(filepath, 'r')
        values = text_file.read().splitlines()
        dictionary = dict()
        lower_bound = 0
        for value in values:
            tokens = re.split('\s+', value)
            dictionary[range(lower_bound, int(tokens[0]))] = float(tokens[1])
            lower_bound = int(tokens[0])
        return dictionary

    @staticmethod
    def get_fee(fees, value):
        for fee_range in fees.keys():
            if math.floor(value) in fee_range:
                return fees[fee_range]

    @staticmethod
    def read_withdrawal(filepath):
        file = open(filepath, "r")
        values = file.read().splitlines()
        dictionary = dict()
        for value in values:
            tokens = re.split('\s+', value)
            dictionary[tokens[0]] = float(tokens[1])
        return dictionary

    @staticmethod
    def get_withdrawal_cost(withdrawal_costs, cryptocurrency):
        return withdrawal_costs.get(cryptocurrency, 0)


bitbay_fees = FeesProvider.read_fees("data/BitbayFees.txt")
bitbay_withdrawal = FeesProvider.read_withdrawal("data/BitbayWithdrawal.txt")
kraken_fees = FeesProvider.read_fees("data/KrakenFees.txt")
kraken_withdrawal = FeesProvider.read_withdrawal("data/KrakenWithdrawal.txt")
