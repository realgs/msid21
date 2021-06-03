from decimal import Decimal
from stock_exchange.Backend.arbitrage_checker import *
from datetime import date, timedelta
import copy
TAX_RATE = 19


class Wallet:
    arbitrage_checker = ArbitrageChecker()

    def __init__(self, assets, base_currency):
        self._assets = assets
        self._base_currency = base_currency

    @classmethod
    def from_json(cls, filepath):
        input = json.loads(open(filepath).read().replace('\n', ''))
        base_currency = input["base_currency"]
        assets = []

        for asset in input["assets"]:
            assets.append(asset)

        return cls(assets, base_currency)

    def evaluate(self, depth=100):
        if depth < 0 or depth > 100:
            return "Wrong depth!"

        print("  {:<18s} {:<14s} {:<18s} {:<11s} {:<14s} {:<18s} {:<s}{:<s}{:<32s}".
              format("STOCK EX. ACRONYM", "NAME", "QUANTITY", "PRICE({})".
                     format(self._base_currency), "VALUE({})".format(self._base_currency),
                     "NET VALUE({})".format(self._base_currency),
                     "" if depth == 100 else "{:<14s}".format(" VALUE {}%".format(depth)),
                     "" if depth == 100 else "{:<18s}".format(" NET VALUE {}%".format(depth)), "ARBITRAGE"))
        print('-' * (164 if depth != 100 else 132))

        previous_total = 0
        current_total = 0

        if depth != 100:
            current_subtotal = 0
            copied_wallet = copy.deepcopy(self)
            total_subtaxes = 0

            for asset in copied_wallet._assets:
                asset["quantity"] = str(float(asset["quantity"]) * depth / 100)

        for asset in self._assets:
            previous_value = float(asset["quantity"]) * float(asset["avg_value"])
            previous_total += previous_value
            trade_info = self._compute_gain(asset["name"])
            current_total += trade_info[0]

            taxes_due = Wallet._compute_taxes(trade_info[0], previous_value, TAX_RATE)
            arbitrages = self._check_all_arbitrages()

            if depth != 100:
                current_subvalue = copied_wallet._compute_gain(asset["name"])[0]
                current_subtotal += current_subvalue
                subtaxes_due = Wallet._compute_taxes(current_subvalue, depth / 100 * previous_value, TAX_RATE)
                total_subtaxes += subtaxes_due

            print("|{:<18s}|{:<14s}|{:<18.6f}|{:<11.2f}|{:<14.2f}|{:<18.2f}|{:<s}{:s}{:<32s}|".
                  format(trade_info[1], asset["name"], float(asset["quantity"]), previous_value, trade_info[0], trade_info[0] - taxes_due,
                         "" if depth == 100 else "{:<13f}|".format(current_subvalue),
                         "" if depth == 100 else str("{:<17f}|".format(current_subvalue - subtaxes_due)),
                         "\n".join("{} {} +{} {}".format(arbitrage[0], arbitrage[1], '%.2E' % Decimal(arbitrage[2]), asset["name"]) for arbitrage in arbitrages if arbitrage[3] == asset["name"])))

        total_taxes = Wallet._compute_taxes(current_total, previous_total, TAX_RATE)

        print('-' * (164 if depth != 100 else 132))
        print(' ' * 53, end='')
        print("|{:<11.2f}|{:<14.2f}|{:<18.2f}|{:<14s}{:<18s}".format(previous_total, current_total, current_total - total_taxes,
            "" if depth == 100 else "{:<13f}|".format(current_subtotal), "" if depth == 100 else "{:<17f}|".format(current_subtotal - total_subtaxes)))
        print(' ' * 53, end='')
        print('-' * (47 if depth == 100 else 79))

    def _check_all_arbitrages(self):
        crypto_assets = []
        cryptocurrencies = []
        arbitrages = []

        for asset in self._assets:
            if asset["type"] == "crypto":
                crypto_assets.append(asset)
                cryptocurrencies.append(asset["name"])

        for asset in crypto_assets:
            for cryptocurrency in cryptocurrencies:
                if asset["stock"] == "BIT" and cryptocurrency != asset["name"]:
                    arbitrages.append(("BB-BITT", "{}{}".format(cryptocurrency, asset["name"]), Wallet.arbitrage_checker.bitbay_bittrex_arbitrage(asset["name"], cryptocurrency, float(asset["quantity"]))[1], asset["name"]))
                elif cryptocurrency != asset["name"]:
                    arbitrages.append(("BITT-BB", "{}{}".format(cryptocurrency, asset["name"]), Wallet.arbitrage_checker.bittrex_bitbay_arbitrage(asset["name"], cryptocurrency, float(asset["quantity"]))[1], asset["name"]))

        for arbitrage in arbitrages:
            if arbitrage[2] == 0:
                arbitrages.remove(arbitrage)

        return arbitrages

    def _compute_gain(self, name):
        offers = self._find_best_offers(name)
        gain = 0

        for offer in offers:
            gain += offer[1] * offer[2]

        return gain, offers[0][0]

    @staticmethod
    def _compute_taxes(income, expense, rate):
        return rate / 100 * (income - expense) if income > expense else 0

    def _find_best_offers(self, name):
        asset = self._get_asset(name)

        if asset == "No such asset is owned!":
            print(asset)

        if asset["type"] == "crypto":
            return self._trade_crypto(asset)
        elif asset["type"] == "currency":
            return self._trade_currency(asset)
        else:
            return self._trade_other(asset)

    def _get_asset(self, name):

        if not any(dictionary["name"] == name for dictionary in self._assets):
            return "No such asset is owned!"

        return [dictionary for dictionary in self._assets if dictionary["name"] == name][0]

    def _trade_crypto(self, asset):
        best_offers = []
        offers = sorted((self._trade_bittrex(asset) + self._trade_bitbay(asset) + self._trade_alpha_vantage(asset)),
                        key=lambda trades: trades[2],
                        reverse=True)

        current_quantity = float(asset["quantity"])

        for offer in offers:
            quantity = min(offer[1], current_quantity)
            current_quantity -= quantity

            best_offers.append((offer[0], quantity, offer[2] * (1 - bittrex_fee / 100)))

            if current_quantity == 0:
                break

        return best_offers if current_quantity == 0 else asset["avg_value"]

    def _trade_bittrex(self, asset):
        best_offers = []
        response = connect("{}getorderbook?market={}-{}&type=buy".format(bittrex, self._base_currency, asset["name"]))

        if not response["success"]:
            return best_offers

        current_quantity = float(asset["quantity"])

        for offer in response["result"]:
            quantity = min(offer["Quantity"], current_quantity)
            current_quantity -= quantity

            best_offers.append(("BTR", quantity, offer["Rate"] * (1 - bittrex_fee / 100)))

            if current_quantity == 0:
                break

        return best_offers

    def _trade_bitbay(self, asset):
        best_offers = []
        response = connect("{}orderbook/{}-{}".format(bitbay, asset["name"], self._base_currency))

        if response["status"] == "Fail":
            return best_offers

        current_quantity = float(asset["quantity"])

        for offer in response["buy"]:
            quantity = min(float(offer["pa"]), current_quantity)
            current_quantity -= quantity

            best_offers.append(("BIT", quantity, float(offer["ra"]) * (1 - bitbay_fee / 100)))

            if current_quantity == 0:
                break

        return best_offers

    def _trade_currency(self, asset):
        best_offers = []
        offers = sorted(self._trade_currency_exchange(asset) + self._trade_alpha_vantage(asset),
                        key=lambda trades: trades[2],
                        reverse=True)

        current_quantity = float(asset["quantity"])

        for offer in offers:
            quantity = min(float(offer[1]), current_quantity)
            current_quantity -= quantity

            best_offers.append((offer[0], quantity, offer[2] * (1 - bittrex_fee / 100)))

            if current_quantity == 0:
                break

        return best_offers if current_quantity == 0 else asset["avg_value"]

    def _trade_alpha_vantage(self, asset):
        response = connect("{}function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}".format
                           (alpha_vantage, asset["name"], self._base_currency, open(
                               "../Resources/alpha_vantage.txt").read()))

        if "Error Message" in response or "Note" in response:
            return [("ALV", float(asset["quantity"]), float(asset["avg_value"]))]

        return [("ALV", float(asset["quantity"]), float(response["Realtime Currency Exchange Rate"]["8. Bid Price"]))]

    def _trade_currency_exchange(self, asset):
        convert_rate = convert_currency(asset["name"], self._base_currency)

        if convert_rate is None:
            convert_rate = asset["avg_value"]

        return [("CEX", asset["quantity"], convert_rate)]

    def _trade_other(self, asset):
        alpha_vantage_result = self._alpha_vantage_stocks(asset)
        eod_data_result = self.eod_data_stocks(asset)

        return alpha_vantage_result if alpha_vantage_result[0][2] > eod_data_result[0][2] else eod_data_result

    def _alpha_vantage_stocks(self, asset):
        response = connect("{}function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&outputsize=1&apikey={}".
                           format(alpha_vantage, asset["name"], open("../Resources/alpha_vantage.txt").read()))

        if "Error Message" in response or "Note" in response:
            return [("ALV", float(asset["quantity"]), float(asset["avg_value"]))]

        date = list(response["Time Series (1min)"].keys())[0]

        return [("ALV", float(asset["quantity"]),
                 float(response["Time Series (1min)"][date]["1. open"]) * convert_currency("USD", self._base_currency))]

    def eod_data_stocks(self, asset):
        key = open("../Resources/eod.txt").read()
        today = date.today()
        yesterday = today - timedelta(days=5)
        response = connect("{}eod/{}.{}?from={}&to={}&api_token={}&period=d&fmt=json".format(eod_data, asset["name"], "US", yesterday, today, key))

        if not response:
            return [("EOD", float(asset["quantity"]), float(asset["avg_value"]))]

        value = response[len(response) - 1]["adjusted_close"]
        return [("EOD", float(asset["quantity"]), value * convert_currency("USD", self._base_currency))]
