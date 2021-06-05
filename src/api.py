from abc import ABC, abstractmethod
import requests

class Api(ABC):
    def __init__(self, name, url):
        super().__init__()
        self.__name = name
        self.__url = url
        self.__orderBook = None

    def isOrderBookFine(self):
        return self.__orderBook != None

    def updateOrderBook(self):
        try:
            self.__orderBook = requests.get(self.__url)
        except requests.exceptions.ConnectionError:
            self.__orderBook = None

    @abstractmethod
    def do_something(self):
        pass

    def version(self):
        return sefl._version
