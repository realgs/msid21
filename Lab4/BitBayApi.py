import json
from Api import Api

BITBAY_TAKER = 0.0037
BITBAY_URL = "https://api.bitbay.net/"


class BitBayApi(Api):
    def __init__(self):
        super().__init__("BitBay", BITBAY_URL)

    def _setFees(self):
        self._fees["taker"] = BITBAY_TAKER

        with open("bitbay_transfer_fees.json", "r") as fees_file:
            transfer_fees = json.load(fees_file)

        self._fees["transfer"] = transfer_fees

    def _setMarkets(self):
        response = Api.request(self._url + "rest/trading/ticker")

        items = response.json()["items"]
        for key, value in items.items():
            c1 = value["market"]["first"]["currency"]
            c2 = value["market"]["second"]["currency"]
            self._markets.add((c1, c2))
