from utils import *

bittrex = "https://api.bittrex.com/api/v1.1/public"
poloniex = "https://poloniex.com/public"


class FeesProvider:

    def __init__(self):
        self._bittrex_withdrawal_fees = {}
        bittrex_response = connect("{}/getcurrencies".format(bittrex))

        for entry in bittrex_response['result']:
            self._bittrex_withdrawal_fees[entry["Currency"]] = entry["TxFee"]

        self._poloniex_withdrawal_fees = {}
        poloniex_response = connect("{}?command=returnCurrencies".format(poloniex))

        for entry in poloniex_response:
            self._poloniex_withdrawal_fees[entry] = poloniex_response[entry]['txFee']

    def bittrex_withdrawal_fee(self, currency):
        return float(self._bittrex_withdrawal_fees[currency])

    def poloniex_withdrawal_fee(self, currency):
        return float(self._poloniex_withdrawal_fees[currency])

    @staticmethod
    def trades_after_fee(trades, fee, type):
        for trade in trades:
            trade[0] = trade[0] * ((1 + (fee / 100)) if type == 'bids' else (1 - fee / 100))
        return trades
