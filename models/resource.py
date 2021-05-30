class Resource:
    def __init__(self,  amount, meanPurchase):
        self.amount = amount
        self.meanPurchase = meanPurchase

    def add(self, resource):
        fullAmount = self.amount + resource.amount
        fullPrice = self.amount * self.meanPurchase + resource.amount * resource.meanPurchase
        self.amount = fullAmount
        self.meanPurchase = fullPrice / fullAmount

    @classmethod
    def fromDict(cls, dataDict):
        return cls(dataDict['amount'], dataDict['meanPurchase'])

    def __repr__(self):
        return {'amount': self.amount, 'meanPurchase': self.meanPurchase}


class ResourceVm:
    def __init__(self, name, amount, meanPurchase, currency):
        self.name = name
        self.amount = amount
        self.meanPurchase = meanPurchase
        self.currency = currency

    def __repr__(self):
        return {'name': self.name, 'amount': self.amount, 'meanPurchase': self.meanPurchase, 'currency': self.currency}


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
    def __init__(self, name, fullProfit, partProfit, amount, part, currency):
        self.name = name
        self.fullProfit = fullProfit
        self.partProfit = partProfit
        self.part = part
        self.currency = currency
        self.fullAmount = amount

    @property
    def partAmount(self):
        return self.fullAmount / 100 * self.part

    def __repr__(self):
        return {'name': self.name,
                'currency': self.currency,
                'full': {'profit': self.fullProfit, 'amount': self.fullAmount},
                'part': {'procent': self.part, 'profit': self.partProfit, 'amount': self.partAmount}}

    def __str__(self):
        return f"name: {self.name}, full profit: {self.fullProfit}, full amount: {self.fullAmount}, part profit: " \
               f"{self.partProfit}, part amount: {self.partAmount}, part: {self.part} %, currency: {self.currency}"


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
    def __init__(self, resourceValue, resourceProfit, meanPurchaseFull, meanPurchasePart):
        self.resourceValue = resourceValue
        self.resourceProfit = resourceProfit
        self.meanPurchaseFull = meanPurchaseFull
        self.meanPurchasePart = meanPurchasePart
        if resourceValue.part != resourceProfit.part or resourceValue.name != resourceProfit.name \
                or resourceValue.currency != resourceProfit.currency:
            print("Error: ResourceStats - value and profit do not match")

    def __repr__(self):
        return {'name': self.resourceValue.name,
                'recommendedSell': self.resourceValue.recommendedSell,
                'currency': self.resourceValue.currency,
                'full': {
                    'amount': self.resourceValue.fullAmount,
                    'meanPurchase': self.meanPurchaseFull,
                    'price': self.resourceValue.fullPrice,
                    'value': self.resourceValue.fullValue,
                    'profit': self.resourceProfit.fullProfit
                },
                'partPercent': self.resourceValue.part,
                'part': {
                    'amount': self.resourceValue.partAmount,
                    'meanPurchase': self.meanPurchasePart,
                    'price': self.resourceValue.partPrice,
                    'value': self.resourceValue.partValue,
                    'profit': self.resourceProfit.partProfit},
                }
