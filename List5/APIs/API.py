import requests
BASE_LIMIT = 20


class Api:
    def __init__(self, name, url, takerFee=None, rate=None, quantity=None, limit=BASE_LIMIT):
        self._name = name
        self._url = url
        self._takerFee = takerFee
        self._rate = rate
        self._quantity = quantity
        self._limit = limit

    def __str__(self):
        return f"{self._name} ({self._url})"

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def takerFee(self):
        return self._takerFee

    @property
    def rate(self):
        return self._rate

    @property
    def quantity(self):
        return self._quantity

    @property
    def markets_list(self):
        raise NotImplementedError()

    @staticmethod
    def data_request(url, headers=None, querystring=None):
        if headers is None and querystring is None:
            response = requests.get(url)
        else:
            response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code != 200:
            return None
        else:
            return response

    def transferFee(self, symbol):
        raise NotImplementedError()

    def orderbook(self, symbol):
        raise NotImplementedError()

    def ticker(self, symbol, base_currency=None):
        raise NotImplementedError()
