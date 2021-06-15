from Api import Api

BITTREX_TAKER = 0.0035
BITTREX_URL = "https://api.bittrex.com/v3/"


class BittrexApi(Api):

    def __init__(self, marketsRange=None):
        super().__init__("Bittrex", "BITT", BITTREX_URL, marketsRange)

    def _setFees(self):
        self._fees["taker"] = BITTREX_TAKER

        response = Api.request(self._url + "currencies")
        items = response.json()

        self._fees["transfer"] = {}

        for item in items:
            symbol = item["symbol"]
            transfer_fee = item["txFee"]
            self._fees["transfer"][symbol] = float(transfer_fee)

    def _setMarkets(self, marketsRange):
        response = Api.request(self._url + "markets")
        items = response.json()

        for item in items:
            status = item["status"]
            if status == "OFFLINE":
                continue
            c1 = item["baseCurrencySymbol"]
            c2 = item["quoteCurrencySymbol"]
            if marketsRange and (c1 not in marketsRange or c2 not in marketsRange):
                continue
            self._markets.add((c1, c2))

    def getOrderbook(self, market):
        result = {"asks": [], "bids": []}

        response = Api.request(self._url + "markets/{0}-{1}/orderbook".format(market[0], market[1]))
        items = response.json()

        asks = items["ask"]

        for ask in asks:
            result["asks"].append((float(ask["quantity"]), float(ask["rate"])))

        bids = items["bid"]

        for bid in bids:
            result["bids"].append((float(bid["quantity"]), float(bid["rate"])))

        return result
