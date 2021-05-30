from stock_exchange.utils import *
import copy
TAX_RATE = 19

class Wallet:

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

        print("  {:<18s} {:<14s} {:<18s} {:<11s} {:<14s} {:<18s}{:<14s}{:<18s}".
              format("STOCK EX. ACRONYM", "NAME", "QUANTITY", "PRICE({})".
                     format(self._base_currency), "VALUE({})".format(self._base_currency),
                     "NET VALUE({})".format(self._base_currency),
                     "" if depth == 100 else " VALUE {}%".format(depth),
                     "" if depth == 100 else " NET VALUE {}%".format(depth)))
        print('-' * (132 if depth != 100 else 100))

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

            if depth != 100:
                current_subvalue = copied_wallet._compute_gain(asset["name"])[0]
                current_subtotal += current_subvalue
                subtaxes_due = Wallet._compute_taxes(current_subvalue, depth / 100 * previous_value, TAX_RATE)
                total_subtaxes += subtaxes_due

            print("|{:<18s}|{:<14s}|{:<18.6f}|{:<11.2f}|{:<14.2f}|{:<18.2f}|{:<14s}{:18s}".
                  format(trade_info[1], asset["name"], float(asset["quantity"]), previous_value, trade_info[0],
                         trade_info[0] - taxes_due, "" if depth == 100 else "{:<13f}|".format(current_subvalue),
                         "" if depth == 100 else str("{:<17f}|".format(current_subvalue - subtaxes_due))))

        total_taxes = Wallet._compute_taxes(current_total, previous_total, TAX_RATE)

        print('-' * (132 if depth != 100 else 100))
        print(' ' * 53, end='')
        print("|{:<11.2f}|{:<14.2f}|{:<18.2f}|{:<14s}{:<18s}".format(previous_total, current_total, current_total - total_taxes,
            "" if depth == 100 else "{:<13f}|".format(current_subtotal), "" if depth == 100 else "{:<17f}|".format(current_subtotal - total_subtaxes)))
        print(' ' * 53, end='')
        print('-' * (47 if depth == 100 else 79))

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
                           (alpha_vantage, asset["name"], self._base_currency, open("alpha_vantage.txt").read()))

        if "Error Message" in response or "Note" in response:
            return [("ALV", float(asset["quantity"]), float(asset["avg_value"]))]

        return [("ALV", float(asset["quantity"]), float(response["Realtime Currency Exchange Rate"]["8. Bid Price"]))]

    def _trade_currency_exchange(self, asset):
        convert_rate = convert_currency(asset["name"], self._base_currency)

        if convert_rate is None:
            convert_rate = asset["avg_value"]

        return [("CEX", asset["quantity"], convert_rate)]

    def _trade_other(self, asset):
        response = connect("{}function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&outputsize=1&apikey={}".
                           format(alpha_vantage, asset["name"], open("alpha_vantage.txt").read()))

        if "Error Message" in response or "Note" in response:
            return [("ALV", float(asset["quantity"]), float(asset["avg_value"]))]

        date = list(response["Time Series (1min)"].keys())[0]

        return [("ALV", float(asset["quantity"]),
                 float(response["Time Series (1min)"][date]["1. open"]) * convert_currency("USD", self._base_currency))]
