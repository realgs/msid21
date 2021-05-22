from services.configurationService import readConfig, saveConfig
from models.resource import Resource, ResourceValue, ResourceProfit, ResourceStats
from services.converter import convertCurrencies
from api import bitbay, bittrex

FILENAME = 'portfolio_data.json'
API_LIST = [bitbay, bittrex]
DEFAULT_VALUE = 'PLN'
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
                recommendedApi = await self.getRecommendedApiForResource(name)
                valuesOfResources.append(ResourceValue(name, fullAmount, 0, 0, self._baseValue, part, recommendedApi))
            else:
                value = await self._calcValue(name, resource.amount, buyFees, part)
                valuesOfResources.append(value)
        return valuesOfResources

    async def getProfit(self, part=100, portfolioValue=None):
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

    async def getRecommendedApiForResource(self, resourceName, orderApiData=None):
        if not orderApiData:
            orderApiData = await self._getSortedOrders(resourceName)
        if len(orderApiData):
            return orderApiData[0]['apiName']
        return 'Not Found'

    @staticmethod
    def _toValidPart(part):
        if part < 0:
            return 0
        if part > 100:
            return 100
        return part

    async def _calcValue(self, name, fullAmount, buyFees, part):
        partValue = self._calcValueForAmount(buyFees, fullAmount / 100 * part)
        fullValue = self._calcValueForAmount(buyFees, fullAmount)

        fullValue = convertCurrencies(DEFAULT_VALUE, self._baseValue, fullValue)
        partValue = convertCurrencies(DEFAULT_VALUE, self._baseValue, partValue)
        recommendedApi = await self.getRecommendedApiForResource(name, buyFees)
        return ResourceValue(name, fullAmount, fullValue, partValue, self._baseValue, part, recommendedApi)

    def _calcValueForAmount(self, buysAndFee, leftAmount):
        value = 0
        for idx in range(0, len(buysAndFee)):
            order, fee, quantity = self._getOrderData(buysAndFee, idx, leftAmount)

            value += quantity * order['price'] * (1 - fee)
            leftAmount -= quantity

            if leftAmount <= 0:
                break
        if leftAmount > 0:
            value += leftAmount * (buysAndFee[-1]['order']['price'] * (1 - buysAndFee[-1]['fee']))
        return value

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
