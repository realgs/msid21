import requests
from abc import ABC, abstractmethod


def request(url):
    headers = {'content-type': 'application/json'}
    response = requests.request("GET", url, headers=headers)
    if 199 < response.status_code < 300:
        return response.json()
    elif 300 < response.status_code < 399:
        raise Exception('Redirection. Need additional action in order to complete request.')
    elif 400 < response.status_code < 499:
        raise Exception('Client error. Server cannot understand the request.')
    elif 500 < response.status_code < 599:
        raise Exception('Server error. Please contact with API providers.')
    return None


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
