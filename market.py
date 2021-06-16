from abc import ABC, abstractmethod


class Market(ABC):
    def __init__(self, name, taker_fee):
        self.name = name
        self.taker_fee = taker_fee

    @abstractmethod
    def get_orderbook(self, pair, limit):
        pass

    @abstractmethod
    def get_pairs(self):
        pass
