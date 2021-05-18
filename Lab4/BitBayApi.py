import json

import requests
from requests import HTTPError

from Api import Api


class BitBayApi(Api):

    BITBAY_TAKER = 0.0037

    def __init__(self):
        super().__init__("BitBay")

    def setFees(self):
        self._fees["taker"] = BitBayApi.BITBAY_TAKER

        with open("bitbay_transfer_fees.json", "r") as fees_file:
            transfer_fees = json.load(fees_file)

        self._fees["transfer"] = transfer_fees

    def setMarkets(self):
        try:
            response = requests.get("https://api.bitbay.net/rest/trading/ticker")

            response.raise_for_status()

            items = response.json()["items"]
            for key, value in items.items():
                c1 = value["market"]["first"]["currency"]
                c2 = value["market"]["second"]["currency"]
                self._markets.add((c1, c2))

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
