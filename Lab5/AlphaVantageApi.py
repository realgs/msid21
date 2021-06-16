import json
from Api import Api

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/"
API_KEY_FILE = "alpha_vantage_api_key.json"
AVAILABLE_RESOURCES = {"BTC", "IBM", "VIVO"}


class AlphaVantageApi(Api):
    def __init__(self, marketsRange=None):
        super().__init__("AlphaVantage", "AV", ALPHA_VANTAGE_URL, marketsRange)
        self._apiKey = None
        self._setApiKey()

    def _setApiKey(self):
        with open("alpha_vantage_api_key.json", "r") as api_key_file:
            api_key = json.load(api_key_file)

        self._apiKey = api_key['key']

    def _setFees(self):
        pass

    def _setMarkets(self, marketsRange):
        pass

    def getOrderbook(self, market):
        if market[1] != "USD" or market[0] not in AVAILABLE_RESOURCES:
            return None

        result = {"asks": [], "bids": []}

        response = Api.request(
            self._url + "query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}".format(market[0],
                                                                                                       self._apiKey))
        items = response.json()

        if 'Error Message' in items.keys() or 'Note' in items.keys():
            return None

        last_refresh = items['Meta Data']['3. Last Refreshed']

        price = float(items['Time Series (5min)'][last_refresh]['4. close'])
        volume = float(items['Time Series (5min)'][last_refresh]['5. volume'])

        result['bids'].append((volume, price))

        return result
