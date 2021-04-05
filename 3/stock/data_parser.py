import krakenex
from stock.fees_provider import *
from stock.currency_exchanger import *

kraken = krakenex.API()
NUMBER_OF_OFFERS = 10


class DataParser:
    currency = ""
    cryptocurrency = ""

    def __init__(self, currency, cryptocurrency):
        self.currency = currency
        self.cryptocurrency = cryptocurrency

    def bitbay_deposit(self, type, currency):
        trades = self.bitbay_trades(type)
        trades_with_fees = self.trades_after_fees(trades, bitbay_fees, currency, "EUR", type)
        return sorted_by_exchange_rate(trades_with_fees, True)

    def bitbay_withdraw(self, type, currency):
        trades = self.bitbay_deposit(type, currency)
        withdrawn_trades = self.trades_after_withdrawal(trades, bitbay_withdrawal)
        return sorted_by_exchange_rate(withdrawn_trades, False)

    def kraken_deposit(self, type, currency):
        trades = self.kraken_trades(type)
        trades_with_fees = self.trades_after_fees(trades, kraken_fees, currency, "USD", type)
        return sorted_by_exchange_rate(trades_with_fees, True)

    def kraken_withdraw(self, type, currency):
        trades = self.kraken_deposit(type, currency)
        withdrawn_trades = self.trades_after_withdrawal(trades, kraken_withdrawal)
        return sorted_by_exchange_rate(withdrawn_trades, False)

    def bitbay_trades(self, type):
        data = connect("https://bitbay.net/API/Public/{0}{1}/orderbook.json".format(self.cryptocurrency, self.currency))
        trades = []
        for trade in data[type][0:min(NUMBER_OF_OFFERS, len(data[type]))]:
            cost = float(trade[0]) * float(trade[1])
            trades.append([cost, float(trade[1])])
        return trades

    def kraken_trades(self, type):
        data = kraken.query_public('Depth', {'pair': self.cryptocurrency + self.currency, 'count': NUMBER_OF_OFFERS})
        trades = []
        for trade in data['result'][next(iter(data['result']))][type]:
            cost = float(trade[0]) * float(trade[1])
            trades.append([cost, float(trade[1])])
        return trades

    def trades_after_fees(self, trades, fees, base_currency, target_currency, type):
        trades_after_fees = []
        for trade in trades:
            fee = FeesProvider.get_fee(fees, CurrencyExchanger.convert(base_currency, target_currency, float(trade[0])))
            value = trade[0] * ((1 + fee / 100) if type == 'asks' else (1 - fee / 100))
            trades_after_fees.append([value, float(trade[1])])
        return trades_after_fees

    def trades_after_withdrawal(self, trades, withdrawal_costs):
        trades_after_withdrawal = []
        for trade in trades:
            quantity = trade[1] - FeesProvider.get_withdrawal_cost(withdrawal_costs, self.cryptocurrency)
            trades_after_withdrawal.append([trade[0], quantity])
        return trades_after_withdrawal
