from abc import abstractmethod, ABC
import requests
from requests import HTTPError


class Api(ABC):
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._fees = {}
        self._markets = set()
        self._setMarkets()
        self._setFees()

    @abstractmethod
    def _setFees(self):
        pass

    @abstractmethod
    def _setMarkets(self):
        pass

    @property
    def fees(self):
        return self._fees

    @property
    def markets(self):
        return self._markets

    @staticmethod
    def request(url):
        response = None

        try:
            response = requests.get(url)
            response.raise_for_status()

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        return response

    def __str__(self):
        return "{0}".format(self._name)
