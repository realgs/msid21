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
    def __init__(self, name, amount, meanPurchase):
        self.name = name
        self.amount = amount
        self.meanPurchase = meanPurchase

    def __repr__(self):
        return {'name': self.name, 'amount': self.amount, 'meanPurchase': self.meanPurchase}


class ResourceValue:
    def __init__(self, name, fullAmount, fullValue, partValue, part, recommendedSell):
        self.name = name
        self.fullAmount = fullAmount
        self.fullValue = fullValue
        self.partValue = partValue
        self.part = part
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
                'recommendedSell': self.recommendedSell,
                'full': {'amount': self.fullAmount, 'price': self.fullPrice, 'value': self.fullValue},
                'part': {'procent': self.part, 'amount': self.partAmount, 'price': self.partPrice, 'value': self.partValue}}


class ResourceProfit:
    def __init__(self, name, fullProfit, partProfit, amount, part):
        self.name = name
        self.fullProfit = fullProfit
        self.partProfit = partProfit
        self.part = part
        self.fullAmount = amount

    @property
    def partAmount(self):
        return self.fullAmount / 100 * self.part

    def __repr__(self):
        return {'name': self.name,
                'full': {'profit': self.fullProfit, 'amount': self.fullAmount},
                'part': {'procent': self.part, 'profit': self.partProfit, 'amount': self.partAmount}}


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


class ResourceStats:
    def __init__(self, resourceValue, resourceProfit, meanPurchaseFull, meanPurchasePart):
        self.resourceValue = resourceValue
        self.resourceProfit = resourceProfit
        self.meanPurchaseFull = meanPurchaseFull
        self.meanPurchasePart = meanPurchasePart
        if resourceValue.part != resourceProfit.part or resourceValue.name != resourceProfit.name:
            print("Error: ResourceStats - value and profit do not match")

    @property
    def name(self):
        return self.resourceValue.name

    def __repr__(self):
        return {'name': self.resourceValue.name,
                'recommendedSell': self.resourceValue.recommendedSell,
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
