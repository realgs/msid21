class Resource:
    def __init__(self, name, amount, meanPurchase):
        self.name = name
        self.amount = amount
        self.meanPurchase = meanPurchase

    def add(self, resource):
        fullAmount = self.amount + resource.amount
        fullPrice = self.amount * self.meanPurchase + resource.amount * resource.meanPurchase
        self.amount = fullAmount
        self.meanPurchase = fullPrice / fullAmount

    @classmethod
    def fromDict(cls, dataDict):
        return cls(dataDict['name'], dataDict['amount'], dataDict['meanPurchase'])

    def toDict(self):
        return {'name': self.name, 'amount': self.amount, 'meanPurchase': self.meanPurchase}

class ResourceValue:
    def __init__(self, name, amount, price, value):
        self.name = name
        self.amount = amount
        self.price = price
        self.value = value