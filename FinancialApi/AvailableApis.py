from dataclasses import field
from Api import BaseApi
import json

PRINT_CANNOT_LOAD_BITBAY_FILE = "Cannot load bitbay withdrawal fees file"


class BitBay(BaseApi):
    withdrawals: dict[str, float] = field(default_factory=dict)

    def __init__(self):
        super().__init__(
            name="BITBAY",
            baseUrl="https://api.bitbay.net/rest/trading",
            marketsPath="/stats",
            orderBookPathPattern="/orderbook-limited/{}-{}/10",
            takerFee=0.0043,
        )
        try:
            with open("bitbay.json", "r") as jsonFile:
                print(self.withdrawals)
                data = json.load(jsonFile)
                print(data)
                self.withdrawals = data
                print(self.withdrawals)
        except:
            print(PRINT_CANNOT_LOAD_BITBAY_FILE)

    def normalizeOffersData(self, data):
        return super().normalizeOffersData(
            data,
            "buy",
            "sell",
            lambda value: (value["ca"], value["ra"])
        )

    def normalizeMarketsData(self, data):
        return super().normalizeMarketsData(
            data,
            lambda value: value["items"],
            lambda value: tuple(value.split("-", 1))
        )

    def getWithdrawalFee(self, market):
        if market[1] in self.withdrawals:
            return self.withdrawals[market[1]]
        else:
            return 0


class Bittrex(BaseApi):
    def __init__(self):
        super().__init__(
            name="BITTREX",
            baseUrl="https://api.bittrex.com/v3",
            marketsPath="/markets",
            orderBookPathPattern="/markets/{}-{}/orderbook",
            takerFee=0.0035
        )

    def normalizeOffersData(self, data):
        return super().normalizeOffersData(
            data,
            "bid",
            "ask",
            lambda value: (value["quantity"], value["rate"])
        )

    def normalizeMarketsData(self, data):
        return super().normalizeMarketsData(
            data,
            lambda value: value,
            lambda value: tuple(value["symbol"].split("-", 1))
        )
