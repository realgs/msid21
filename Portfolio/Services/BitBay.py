from Services.BaseService import BaseService
from dataclasses import field
import json

PRINT_CANNOT_LOAD_BITBAY_FILE = "Cannot load bitbay withdrawal fees file"


class BitBay(BaseService):
    withdrawals: dict[str, float] = field(default_factory=dict)

    def __init__(self):
        super().__init__(
            name="BITBAY",
            baseUrl="https://api.bitbay.net/rest/trading",
            marketsPath="/stats",
            orderBookPathPattern="/orderbook-limited/{}-{}/10",
            isArbitragePossible=True,
            takerFee=0.0043,
        )
        try:
            with open("bitbay.json", "r") as jsonFile:
                data = json.load(jsonFile)
                self.withdrawals = data
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


