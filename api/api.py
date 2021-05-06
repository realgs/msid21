import requests

BASE_LIMIT = 10

class Api:
    def __init__(self, name, url, limit = BASE_LIMIT):
        self._name = name
        self._url = url
        self._limit = limit

    def __str__(self):
        return f"{self._name} ({self._url})"

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    def request(self, url):
        headers = {
            'content-type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise ConnectionError(response.reason)

    @property
    def transactionFee(self):
        raise NotImplementedError()

    def withdrawalFee(self, symbol):
        raise NotImplementedError()

    @property
    def markets(self):
        raise NotImplementedError()

    def orderbook(self, symbol):
        raise NotImplementedError()

