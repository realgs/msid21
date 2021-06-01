from models.resource import Resource


class ResourceQueue:
    def __init__(self, name, resources=[]):
        self.resources = resources
        self.name = name
        self.__amountLeft = None

    @classmethod
    def fromJson(cls, jsonRepr):
        name = jsonRepr['name']
        resources = [Resource.fromDict(resourceDict) for resourceDict in jsonRepr['data']]
        return cls(name, resources)

    def __repr__(self):
        return {'name': self.name, 'data': [resource.__repr__() for resource in self.resources]}

    def push(self, amount, price):
        self.resources.append(Resource(amount, price))
        self.__amountLeft = None

    def amountLeft(self):
        if not self.__amountLeft:
            sumAmount = 0
            for res in self.resources:
                sumAmount += res.amount
            self.__amountLeft = sumAmount
        return self.__amountLeft

    def meanPurchase(self, part=100):
        if self.isEmpty():
            return 0
        neededAmount = self.amountLeft() / 100 * part
        restAmount, sumValue = neededAmount, 0
        for res in self.resources:
            if res.amount <= restAmount:
                sumValue += res.amount * res.meanPurchase
                restAmount -= res.amount
            else:
                sumValue += restAmount * res.meanPurchase
        return sumValue / neededAmount

    def isEmpty(self):
        return self.amountLeft() == 0

    def tryPop(self, amount):
        if amount > self.amountLeft():
            return False
        fullValue = 0
        while amount > 0:
            if amount >= self.resources[0].amount:
                resource = self.resources.pop()
                fullValue += resource.amount * resource.meanPurchase
                amount -= resource.amount
            else:
                resource = self.resources[0]
                fullValue += amount * resource.meanPurchase
                resource.amount -= amount
                amount = 0
        self.__amountLeft = None
        return True
