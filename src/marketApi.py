from decimal import Decimal
import requests
import consts

class Market():
    def __init__(self, name, marketType):
        self.__name = name
        self.__marketType = marketType

    def __str__(self):
        return self.__name

    @property
    def name(self):
        return self.__name

    @property
    def marketType(self):
        return self.__marketType

    def getSellPrice(self, symbol, volume, percentage):
        raise NotImplementedError
        