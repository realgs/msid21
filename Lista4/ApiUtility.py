import requests


BASE_LIMIT = 30


class ApiUtility:
    def __init__(self, name, url, limit=BASE_LIMIT):
        self._stock_name = name
        self._api_url = url
        self._offers_limit = limit

    @property
    def stock_name(self):
        return self._stock_name

    @property
    def api_url(self):
        return self._api_url

    def get_taker_fee(self):
        raise NotImplementedError()

    def get_transfer_fee(self, symbol):
        raise NotImplementedError()

    def get_markets(self):
        raise NotImplementedError()

    def request_to_api(self, url):
        headers = {'content-type': 'application/json'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise ConnectionError(response.reason)

    def get_orderbook(self, symbol):
        raise NotImplementedError()

    def __str__(self):
        return f"{self._stock_name} ({self._api_url})"
