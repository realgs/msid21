from services.configurationService import readConfig, saveConfig
from models.resource import Resource, ResourceValue, ResourceProfit, ResourceStats
from services.converter import convertCurrencies
from api import bitbay, bittrex

FILENAME = 'portfolio_data.json'
API_LIST = [bitbay, bittrex]
DEFAULT_VALUE = 'USD'
SUCCESS_KEY = 'success'
COUNTRY_PROFIT_FEE = 0.19


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

    def save(self):
        data = {'baseValue': self._baseValue, 'resources': [resource.toDict() for _, resource in self._resources.items()]}
        saveConfig(self._owner+"_"+FILENAME, data)

    def addResource(self, resource):
        if resource.name in self._resources:
            self._resources[resource.name].add(resource)
        else:
            self._resources[resource.name] = resource

    async def getStats(self, part=100):
        part = self._toValidPart(part)
        portfolioValue = await self.portfolioValue(part)
        nameToResourceValue, stats = {}, []
        for resourceValue in portfolioValue:
            nameToResourceValue[resourceValue.name] = resourceValue

        profits = await self.getProfit(part, portfolioValue)
        for profit in profits:
            value = nameToResourceValue[profit.name]
            resource = self._resources[profit.name]
            stats.append(ResourceStats(value, profit, resource.meanPurchase))

        return stats

    async def portfolioValue(self, part=100):
        part = self._toValidPart(part)
        valuesOfResources = []
        for _, resource in self._resources.items():
            buyFees = await self._getSortedOrders(resource.name)
            name, fullAmount = resource.name, resource.amount / 100 * part
            if not buyFees:
                valuesOfResources.append(ResourceValue(name, fullAmount, 0, 0, self._baseValue, part))
            else:
                value = self._calcValue(name, resource.amount, buyFees, part)
                valuesOfResources.append(value)
        return valuesOfResources

    async def getProfit(self, part=100, portfolioValue=None):
        # TODO: Kwota JEJ nabycia
        part = self._toValidPart(part)
        if not portfolioValue:
            portfolioValue = await self.portfolioValue(part)
        profits = []
        for resourceValue in portfolioValue:
            fullValue, partValue = resourceValue.fullValue, resourceValue.partValue
            fullAmount, partAmount = resourceValue.fullAmount, resourceValue.fullAmount / 100 * part
            meanPurchase = self._resources[resourceValue.name].meanPurchase
            fullProfit = (fullValue - meanPurchase * fullAmount) * (1 - COUNTRY_PROFIT_FEE)
            partProfit = (partValue - meanPurchase * partAmount) * (1 - COUNTRY_PROFIT_FEE)
            profits.append(ResourceProfit(resourceValue.name, fullProfit, partProfit, part))
        return profits

    @staticmethod
    def _toValidPart(part):
        if part < 0:
            return 0
        if part > 100:
            return 100
        return part

    def _calcValue(self, name, fullAmount, buyFees, part):
        leftPartAmount, leftFullAmount = fullAmount / 100 * part, fullAmount
        partValue, fullValue = 0, 0
        recommendedSell = buyFees[0]['apiName']

        stopIdx = 0
        for idx in range(0, len(buyFees)):
            order, fee, quantity = self._getOrderData(buyFees, idx, leftPartAmount)

            partValue += quantity * order['price'] * (1 - fee)
            fullValue += quantity * order['price'] * (1 - fee)
            leftPartAmount -= quantity
            leftFullAmount -= quantity

            if leftPartAmount <= 0:
                stopIdx = idx
                order['quantity'] -= quantity
                break

        for idx in range(stopIdx, len(buyFees)):
            order, fee, quantity = self._getOrderData(buyFees, idx, leftFullAmount)
            fullValue += quantity * order['price'] * (1 - fee)
            leftFullAmount -= quantity

            if leftFullAmount <= 0:
                break
        # Two cases:
        # 1. if the amount of resources will exceed the capabilities of the api
        # 2. if api does not provide an orderbook, it is obliged to return one price according to which the value will be calculated
        if leftPartAmount > 0:
            partValue += leftPartAmount * (buyFees[-1]['order']['price'] * (1 - buyFees[-1]['fee']))
        if leftFullAmount > 0:
            fullValue += leftFullAmount * (buyFees[-1]['order']['price'] * (1 - buyFees[-1]['fee']))

        fullValue = convertCurrencies(DEFAULT_VALUE, self._baseValue, fullValue)
        partValue = convertCurrencies(DEFAULT_VALUE, self._baseValue, partValue)
        return ResourceValue(name, fullAmount, fullValue, partValue, self._baseValue, part, recommendedSell)

    @staticmethod
    def _getOrderData(buyFees, idx, leftAmount):
        orderData = buyFees[idx]
        order, fee = orderData['order'], orderData['fee']
        quantity = min(leftAmount, float(order['quantity']))
        return order, fee, quantity

    @staticmethod
    async def _getSortedOrders(resourceName):
        allOrders = [(await api.getBestOrders((resourceName, DEFAULT_VALUE)), api.getTakerFee(), api.getName()) for api in API_LIST]
        buyFees = []

        for orders, fee, apiName in allOrders:
            if orders[SUCCESS_KEY]:
                for order in orders['buys']:
                    buyFees.append({'order': order, 'fee': fee, 'apiName': apiName})
        return sorted(buyFees, key=lambda buyFee: buyFee['order']['price'], reverse=True)
