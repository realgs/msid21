from Services.BaseService import BaseService


class Bittrex(BaseService):
    def __init__(self):
        super().__init__(
            name="BITTREX",
            baseUrl="https://api.bittrex.com/v3",
            marketsPath="/markets",
            orderBookPathPattern="/markets/{}-{}/orderbook",
            isArbitragePossible=True,
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