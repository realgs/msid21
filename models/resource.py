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
    def __init__(self, name, fullAmount, fullValue, partValue, currency, part, recommendedSell):
        self.name = name
        self.fullAmount = fullAmount
        self.fullValue = fullValue
        self.partValue = partValue
        self.part = part
        self.currency = currency
        self.recommendedSell = recommendedSell

    @property
    def fullPrice(self):
        return self.fullValue / self.fullAmount

    @property
    def partAmount(self):
        return self.fullAmount * self.part / 100

    @property
    def partPrice(self):
        return self.partValue / self.partAmount

    def __str__(self):
        return f"name: {self.name}, full amount: {self.fullAmount}, full price: {self.fullPrice}, " \
               f"full value: {self.fullValue} {self.currency}, part: {self.part} %, " \
               f"part price: {self.partPrice}, part value: {self.partValue}, recommended sell: {self.recommendedSell}"


class ResourceProfit:
    def __init__(self, name, fullProfit, partProfit, part):
        self.name = name
        self.fullProfit = fullProfit
        self.partProfit = partProfit
        self.part = part

    def __str__(self):
        return f"name: {self.name},full profit: {self.fullProfit}, part profit: {self.partProfit}, part: {self.part} %, "


class ResourceStats:
    def __init__(self, resourceValue, resourceProfit, meanPurchase):
        self.resourceValue = resourceValue
        self.resourceProfit = resourceProfit
        self.meanPurchase = meanPurchase
        if resourceValue.part != resourceProfit.part or resourceValue.name != resourceProfit.name:
            print("Error: ResourceStats - value and profit do not match")

    def getStats(self):
        return {'name': self.resourceValue.name,
                'meanPurchase': self.meanPurchase,
                'recommendedSell': self.resourceValue.recommendedSell,
                'full': {'amount': self.resourceValue.fullAmount, 'price': self.resourceValue.fullPrice, 'value': self.resourceValue.fullValue, 'profit': self.resourceProfit.fullProfit},
                'part percent': self.resourceValue.part,
                'part': {'amount': self.resourceValue.partAmount, 'price': self.resourceValue.partPrice, 'value': self.resourceValue.partValue, 'profit': self.resourceProfit.partProfit}}
