class Resource:
    def __init__(self, name, amount, meanPurchase):
        self._name = name
        self._amount = amount
        self._meanPurchase = meanPurchase

    @property
    def name(self):
        return self._name

    @property
    def amount(self):
        return self._amount

    @property
    def meanPurchase(self):
        return self._meanPurchase

    def add(self, resource):
        fullAmount = self._amount + resource.amount
        fullPrice = self._amount * self._meanPurchase + resource.amount * resource.meanPurchase
        self._amount = fullAmount
        self._meanPurchase = fullPrice / fullAmount

    @classmethod
    def fromDict(cls, dataDict):
        return cls(dataDict['name'], dataDict['amount'], dataDict['meanPurchase'])

    def toDict(self):
        return {'name': self._name, 'amount': self._amount, 'meanPurchase': self._meanPurchase}
