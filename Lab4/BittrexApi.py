from Api import Api

BITTREX_TAKER = 0.0035
BITTREX_URL = "https://api.bittrex.com/v3/"


class BittrexApi(Api):

    def __init__(self):
        super().__init__("Bittrex", BITTREX_URL)

    def _setFees(self):
        self._fees["taker"] = BITTREX_TAKER

        response = Api.request(self._url + "currencies")
        items = response.json()

        self._fees["transfer"] = {}

        for item in items:
            symbol = item["symbol"]
            transfer_fee = item["txFee"]
            self._fees["transfer"][symbol] = transfer_fee

    def _setMarkets(self):
        response = Api.request(self._url + "markets")
        items = response.json()

        for item in items:
            c1 = item["baseCurrencySymbol"]
            c2 = item["quoteCurrencySymbol"]
            self._markets.add((c1, c2))
