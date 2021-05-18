from abc import ABC

from Api import Api


class BittrexApi(Api, ABC):
    def setFees(self):
        pass

    def setMarkets(self):
        pass
