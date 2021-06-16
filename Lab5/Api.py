from abc import abstractmethod, ABC
import requests
from requests import HTTPError


class Api(ABC):
    def __init__(self, name, sign, url, marketsRange):
        self._name = name
        self._sign = sign
        self._url = url
        self._fees = {}
        self._markets = set()
        self._setFees()
        self._setMarkets(marketsRange)

    @abstractmethod
    def _setFees(self):
        pass

    @abstractmethod
    def _setMarkets(self, marketsRange):
        pass

    @abstractmethod
    def getOrderbook(self, market):
        pass

    @property
    def sign(self):
        return self._sign

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
            pass
        except Exception as err:
            pass

        return response

    def __str__(self):
        return "{0}".format(self._name)
