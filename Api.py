import requests
from abc import ABC, abstractmethod


class Api(ABC):
    def __init__(self, name, base_url):
        self.__name = name
        self.__base_url = base_url

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__base_url

    def __is_valid_code(self, code):
        return 199 < code < 300

    def request(self, url):
        headers = {'content-type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        if self.__is_valid_code(response.status_code):
            return response.json()
        elif 300 < response.status_code < 399:
            raise Exception('Redirection. Need additional action in order to complete request.')
        elif 400 < response.status_code < 499:
            raise Exception('Client error. Server cannot understand the request.')
        elif 500 < response.status_code < 599:
            raise Exception('Server error. Please contact with API providers.')
        return None

    @abstractmethod
    def markets(self):
        pass

    @abstractmethod
    def orderbook(self, first, second):
        pass

    @abstractmethod
    def transfer_fee(self, currency):
        pass

    @abstractmethod
    def taker_fee(self):
        pass
