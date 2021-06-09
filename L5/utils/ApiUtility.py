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

    def if_orderbook_supported(self):
        raise NotImplementedError()

    def request_to_api(self, url):
        headers = {'content-type': 'application/json'}
        response = requests.get(url, headers=headers)

        if 199 < response.status_code < 300:
            return response.json()
        elif 300 < response.status_code < 399:
            raise Exception('Redirection. Need additional action in order to complete request.')
        elif 400 < response.status_code < 499:
            raise Exception(f'Client error. Can not understand the request. Code {response.status_code}')
        elif 500 < response.status_code < 599:
            raise Exception('Server error. Please contact the API providers.')
        return None

    def get_orderbook(self, symbol):
        raise NotImplementedError()

    def __str__(self):
        return f"{self._stock_name} ({self._api_url})"
