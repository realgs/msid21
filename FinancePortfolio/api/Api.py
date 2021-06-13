import requests

DEFAULT_LIMIT = 50
API_TYPES = ['stock', 'cryptocurrency', 'currency']


class Api:

    def __init__(self, name, base_url, api_type, limit=DEFAULT_LIMIT, fees=None):
        self._name = name
        self._base_url = base_url
        self._api_type = api_type
        self._limit = limit
        self._fees = fees

    @property
    def name(self):
        return self._name

    @property
    def baseUrl(self):
        return self._base_url

    @property
    def apiType(self):
        return self._api_type

    @property
    def limit(self):
        return self._limit

    @property
    def fees(self):
        return self._fees

    def getApiResponse(self, url, headers=None):
        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            print(f'Failed to establish connection with {url}')
        else:
            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                print('Sorry, no data found: ', response.status_code, ' ', response.reason)
                return None
