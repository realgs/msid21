from abc import abstractmethod, ABC


class Api(ABC):
    def __init__(self, name):
        self._name = name
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

    def __str__(self):
        return "{0}".format(self._name)
