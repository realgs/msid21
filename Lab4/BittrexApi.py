import requests
from requests import HTTPError

from Api import Api


class BittrexApi(Api):
    BITTREX_TAKER = 0.0035

    def __init__(self):
        super().__init__("Bittrex")

    def setFees(self):
        self._fees["taker"] = BittrexApi.BITTREX_TAKER
        try:
            response = requests.get("https://api.bittrex.com/v3/currencies")

            response.raise_for_status()
            items = response.json()

            self._fees["transfer"] = {}

            for item in items:
                symbol = item["symbol"]
                transfer_fee = item["txFee"]
                self._fees["transfer"][symbol] = transfer_fee

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    def setMarkets(self):
        try:
            response = requests.get("https://api.bittrex.com/v3/markets")

            response.raise_for_status()
            items = response.json()

            for item in items:
                c1 = item["baseCurrencySymbol"]
                c2 = item["quoteCurrencySymbol"]
                self._markets.add((c1, c2))

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
