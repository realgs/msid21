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

    def __repr__(self):
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

    def __repr__(self):
        return {'name': self.name,
                'currency': self.currency,
                'recommendedSell': self.recommendedSell,
                'full': {'amount': self.fullAmount, 'price': self.fullPrice, 'value': self.fullValue},
                'part': {'procent': self.part, 'amount': self.partAmount, 'price': self.partPrice, 'value': self.partValue}}

    def __str__(self):
        return f"name: {self.name}, full amount: {self.fullAmount}, full price: {self.fullPrice}, " \
               f"full value: {self.fullValue} {self.currency}, part: {self.part} %, " \
               f"part price: {self.partPrice}, part value: {self.partValue}, recommended sell: {self.recommendedSell}"


class ResourceProfit:
    def __init__(self, name, fullProfit, partProfit, part, currency):
        self.name = name
        self.fullProfit = fullProfit
        self.partProfit = partProfit
        self.part = part
        self.currency = currency

    def __repr__(self):
        return {'name': self.name,
                'currency': self.currency,
                'full': {'profit': self.fullProfit},
                'part': {'procent': self.part, 'profit': self.partProfit}}

    def __str__(self):
        return f"name: {self.name},full profit: {self.fullProfit}, part profit: {self.partProfit}, part: {self.part} %, currency: {self.currency}"


class ResourceArbitration:
    def __init__(self, currency1, currency2, api1, api2, rate, profit, quantity):
        self.currency1 = currency1
        self.currency2 = currency2
        self.api1 = api1
        self.api2 = api2
        self.rate = rate
        self.profit = profit
        self.quantity = quantity

    def __repr__(self):
        return {'currency1': self.currency1, 'currency2': self.currency2, 'api1': self.api1, 'api2': self.api2,
                'rate': self.rate, 'profit': self.profit, 'quantity': self.quantity}

    def __str__(self):
        return f"currency1: {self.currency1}, currency2: {self.currency2}, api1: {self.api1}, api2: {self.api2}, " \
               f"rate: {self.rate}, profit: {self.profit}, quantity: {self.quantity}"


class ResourceStats:
    def __init__(self, resourceValue, resourceProfit, meanPurchase, arbitration):
        self.resourceValue = resourceValue
        self.resourceProfit = resourceProfit
        self.meanPurchase = meanPurchase
        self.arbitration = arbitration
        if resourceValue.part != resourceProfit.part or resourceValue.name != resourceProfit.name \
                or resourceValue.currency != resourceProfit.currency:
            print("Error: ResourceStats - value and profit do not match")

    def __repr__(self):
        return {'name': self.resourceValue.name,
                'meanPurchase': self.meanPurchase,
                'recommendedSell': self.resourceValue.recommendedSell,
                'currency': self.resourceValue.currency,
                'value': {
                    'full': {'amount': self.resourceValue.fullAmount, 'price': self.resourceValue.fullPrice,
                             'value': self.resourceValue.fullValue, 'profit': self.resourceProfit.fullProfit},
                    'part percent': self.resourceValue.part,
                    'part': {'amount': self.resourceValue.partAmount, 'price': self.resourceValue.partPrice,
                             'value': self.resourceValue.partValue, 'profit': self.resourceProfit.partProfit},
                },
                'arbitration': [arbitration.__repr__() for arbitration in self.arbitration]}
