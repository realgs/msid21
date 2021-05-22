from services.configurationService import readConfig, saveConfig
from models.resource import Resource, ResourceValue, ResourceProfit, ResourceStats, ResourceArbitration
from api import bitbay, bittrex
from services.profitService import ProfitService

FILENAME = 'portfolio_data.json'
API_LIST = [bitbay, bittrex]
DEFAULT_VALUE = 'USD'
SUCCESS_KEY = 'success'
COUNTRY_PROFIT_FEE = 0.19


class Portfolio:
    def __init__(self, owner, baseValue, cantorService):
        self._owner = owner
        self._baseValue = baseValue
        self.cantorService = cantorService
        self._resources = {}
        self._apiCrossProfitServices = None

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
            name = profit.name
            value = nameToResourceValue[name]
            resource = self._resources[name]
            allArbitration = await self.getAllArbitration(name)
            stats.append(ResourceStats(value, profit, resource.meanPurchase, allArbitration))

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
            meanPurchase = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, self._resources[resourceValue.name].meanPurchase)
            fullProfit = (fullValue - meanPurchase * fullAmount) * (1 - COUNTRY_PROFIT_FEE)
            partProfit = (partValue - meanPurchase * partAmount) * (1 - COUNTRY_PROFIT_FEE)
            profits.append(ResourceProfit(resourceValue.name, fullProfit, partProfit, part, self._baseValue))
        return profits

    async def getRecommendedApiForResource(self, resourceName, orderApiData=None):
        if not orderApiData:
            orderApiData = await self._getSortedOrders(resourceName)
        if len(orderApiData):
            return orderApiData[0]['apiName']
        return 'Not Found'

    async def getAllArbitration(self, resource=None):
        resourcePairs = self._getResourcesCrossProduct()
        if resource:
            resourcePairs = [pair for pair in self._getResourcesCrossProduct() if pair[0] == resource or pair[1] == resource]
        resourcesProfits = []
        for pair in resourcePairs:
            profits = await self.getArbitration(pair[0], pair[1])
            for profit in profits:
                resourcesProfits.append(ResourceArbitration(
                    profit['currencies'][0], profit['currencies'][1], profit['names'][0], profit['names'][1], profit['rate'], profit['profit'], profit['quantity']))
        return resourcesProfits

    async def getArbitration(self, resourceName1, resourceName2):
        if resourceName1 not in self._resources or resourceName2 not in self._resources:
            print(f'Warning - Portfolio - getArbitration: request with not existing resources: {resourceName1} or {resourceName2}')
            return []

        availableProfitServices = await self._getApiCrossProfitServices()
        allProfits = []
        for profitService in availableProfitServices:
            # data = await profitService.getPossibleArbitration({'currency1': resourceName1, 'currency2': resourceName2}, True)
            data = await profitService.getPossibleArbitration({'currency1': resourceName1, 'currency2': resourceName2})
            if data and len(data):
                allProfits.append(data[0])
        allProfits = sorted(allProfits, key=lambda data: data['rate'], reverse=True)
        return self._getPossibleProfits(allProfits, resourceName1, resourceName2)

    def _getPossibleProfits(self, allProfits, resourceName1, resourceName2):
        amount = min(self._resources[resourceName1].amount, self._resources[resourceName2].amount)
        bestArbitration = []
        for profit in allProfits:
            quantity = min(amount, profit['quantity'])
            profit['quantity'] = quantity
            bestArbitration.append(profit)
            amount -= quantity
            if amount < 0:
                break
        return bestArbitration

    async def _getApiCrossProfitServices(self):
        if not self._apiCrossProfitServices:
            self._apiCrossProfitServices = []
            for idx1 in range(0, len(API_LIST)):
                api1 = API_LIST[idx1]
                for idx2 in range(idx1 + 1, len(API_LIST)):
                    api2 = API_LIST[idx2]
                    profitService = ProfitService(api1, api2)
                    commonMarkets = await profitService.commonMarkets
                    if commonMarkets:
                        self._apiCrossProfitServices.append(profitService)
        return self._apiCrossProfitServices

    def _getResourcesCrossProduct(self):
        resourcePairs = []
        resourcesList = [name for name in self._resources]
        for resource1 in resourcesList:
            for resource2 in resourcesList:
                if resource1 != resource2:
                    resourcePairs.append((resource1, resource2))
        return resourcePairs

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

        fullValue = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, fullValue)
        partValue = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, partValue)
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
