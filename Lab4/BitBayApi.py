import json
from Api import Api

BITBAY_TAKER = 0.0043
BITBAY_URL = "https://api.bitbay.net/rest/trading/"


class BitBayApi(Api):
    def __init__(self):
        super().__init__("BitBay", BITBAY_URL)

    def _setFees(self):
        self._fees["taker"] = BITBAY_TAKER

        with open("bitbay_transfer_fees.json", "r") as fees_file:
            transfer_fees = json.load(fees_file)

        self._fees["transfer"] = transfer_fees

    def _setMarkets(self):
        response = Api.request(self._url + "ticker")
        items = response.json()["items"]

        symbols = list(map(lambda x: x, self.fees["transfer"].keys()))

        for key, value in items.items():
            c1 = value["market"]["first"]["currency"]
            c2 = value["market"]["second"]["currency"]
            if c1 not in symbols or c2 not in symbols:
                continue
            self._markets.add((c1, c2))

    def getOrderbook(self, market):
        result = {"asks": [], "bids": []}

        response = Api.request(self._url + "orderbook/{0}-{1}".format(market[0], market[1]))
        items = response.json()

        asks = items["sell"]

        for ask in asks:
            result["asks"].append((float(ask["ca"]), float(ask["ra"])))

        bids = items["buy"]

        for bid in bids:
            result["bids"].append((float(bid["ca"]), float(bid["ra"])))

        return result
