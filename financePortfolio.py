from services.configurationService import readConfig, saveConfig
from models.resource import Resource, ResourceValue
from services.converter import convertCurrencies
from api import bitbay, bittrex

FILENAME = 'portfolio_data.json'
API_LIST = [bitbay, bittrex]
DEFAULT_VALUE = 'USD'
SUCCESS_KEY = 'success'


class Portfolio:
    def __init__(self, owner, baseValue):
        self._owner = owner
        self._baseValue = baseValue
        self._resources = {}

    def read(self):
        data = readConfig(self._owner+"_"+FILENAME)
        if data:
            self._resources = {resource['name']: Resource.fromDict(resource) for resource in data['resources']}
            return True
        else:
            return False

    def addResource(self, resource):
        if resource.name in self._resources:
            self._resources[resource.name].add(resource)
        else:
            self._resources[resource.name] = resource

    async def fullPortfolioValue(self):
        return await self.portfolioValue(100)

    async def portfolioValue(self, part):
        valuesOfResources = []
        for _, resource in self._resources.items():
            buyFees = await self._getSortedOrders(resource.name)
            name, fullAmount = resource.name, resource.amount * part / 100
            if not buyFees:
                valuesOfResources.append(ResourceValue(name, fullAmount, 0, self._baseValue, part))
            else:
                value = self._calcValue(name, fullAmount, resource.amount, buyFees, part)
                valuesOfResources.append(value)
        return valuesOfResources

    def _calcValue(self, name, fullAmount, amount, buyFees, part):
        leftAmount = amount
        fullValue = 0

        for orderData in buyFees:
            order, fee = orderData['order'], orderData['fee']
            quantity = min(leftAmount, float(order['quantity']))
            fullValue += quantity * order['price'] * (1 - fee)
            leftAmount -= quantity
            if leftAmount <= 0:
                break
        # Two cases:
        # 1. if the amount of resources will exceed the capabilities of the api
        # 2. if api does not provide an orderbook, it is obliged to return one price according to which the value will be calculated
        if leftAmount > 0:
            fullValue += leftAmount * (buyFees[-1]['order']['price'] * (1 - buyFees[-1]['fee']))

        fullValue = convertCurrencies(DEFAULT_VALUE, self._baseValue, fullValue)
        return ResourceValue(name, fullAmount, fullValue, self._baseValue, part)

    @staticmethod
    async def _getSortedOrders(resourceName):
        allOrders = [(await api.getBestOrders((resourceName, DEFAULT_VALUE)), api.getTakerFee()) for api in API_LIST]
        buyFees = []

        for orders, fee in allOrders:
            if orders[SUCCESS_KEY]:
                for order in orders['buys']:
                    buyFees.append({'order': order, 'fee': fee})
        return sorted(buyFees, key=lambda buyFee: buyFee['order']['price'], reverse=True)

    def save(self):
        data = {'baseValue': self._baseValue, 'resources': [resource.toDict() for _,resource in self._resources.items()]}
        saveConfig(self._owner+"_"+FILENAME, data)
