class Api:
    def __init__(self, name, takerFee=0):
        self.name = name
        self.takerFee = takerFee

    def getName(self):
        return self.name

    def getTakerFee(self):
        return self.takerFee

    async def getTransferFee(self, resource):
        raise NotImplemented

    async def getBestOrders(self, resources, amount=None):
        raise NotImplemented

    async def getAvailableMarkets(self):
        raise NotImplemented
