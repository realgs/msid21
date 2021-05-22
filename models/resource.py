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
    def __init__(self, name, amount, value, currency, part):
        self.name = name
        self.amount = amount
        self.value = value
        self.part = part
        self.currency = currency

    @property
    def price(self):
        return self.value / self.amount

    def __str__(self):
        return f"name: {self.name}, amount: {self.amount}, price: {self.price}, value: {str(self.value) + ' ' + self.currency}, part: {self.part}"
