import asyncio
from services.configurationService import readConfig, saveConfig
from services.valueService import ValueService
from models.resource import ResourceVm, ResourceValue, ResourceProfit, ResourceStats, ResourceArbitration
from models.resourceQueue import ResourceQueue
from services.arbitrationService import ArbitrationService

FILENAME = 'portfolio_data.json'
DEFAULT_VALUE = 'USD'
SUCCESS_KEY = 'success'
DEFAULT_COUNTRY_PROFIT_FEE = 0.19


class Portfolio:
    def __init__(self, owner, cantorService, apiList):
        self._owner = owner
        self._baseValue = DEFAULT_VALUE
        self.cantorService = cantorService
        self._resources = {}
        self._apiList = apiList
        self._countryProfitFee = DEFAULT_COUNTRY_PROFIT_FEE
        self._apiCrossProfitServices = None
        self._valueService = ValueService(DEFAULT_VALUE, self._apiList.copy(), SUCCESS_KEY)

    def read(self):
        data = readConfig(self._owner+"_"+FILENAME)
        if data:
            self._resources = {resourceRepr['name']: ResourceQueue.fromJson(resourceRepr) for resourceRepr in data['resources']}
            self._baseValue = data['baseValue']
            self._countryProfitFee = data['countryProfitFee']
            return True
        return False

    def save(self):
        data = {'baseValue': self._baseValue, 'countryProfitFee': self._countryProfitFee,
                'resources': [resource.__repr__() for _, resource in self._resources.items()]}
        return saveConfig(self._owner+"_"+FILENAME, data)

    @property
    def countryProfitFee(self):
        return self._countryProfitFee

    def setCountryProfitFee(self, fee):
        if fee < 0:
            print(f"Warning - Portfolio - setCountryProfitFee: incorrect fee: {fee}")
            fee = 0
        elif fee > 1:
            print(f"Warning - Portfolio - setCountryProfitFee: incorrect fee: {fee}")
            fee = 1
        self._countryProfitFee = fee

    @property
    def baseValue(self):
        return self._baseValue

    def setBaseValue(self, currency):
        self._baseValue = currency

    async def availableApi(self):
        result = []
        for api in self._apiList:
            markets = await api.available()
            if markets['success']:
                markets = sorted(markets['markets'], key=lambda m: (m['currency1'], m['currency2']))
                result.append({'name': api.name(), 'type': api.type(), 'markets': markets})
        return result

    @property
    async def resources(self):
        result = [ResourceVm(name, resourceQueue.amountLeft(), await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, resourceQueue.meanPurchase())) for name, resourceQueue in self._resources.items()]
        return sorted(result, key=lambda res: res.name), self._baseValue

    async def addResource(self, name, amount, price):
        if amount > 0 and price > 0:
            price = await self.cantorService.convertCurrencies(self._baseValue, DEFAULT_VALUE, price)
            if name in self._resources:
                self._resources[name].push(amount, price)
            else:
                newQueue = ResourceQueue(name, [])
                newQueue.push(amount, price)
                self._resources[name] = newQueue
            return True
        return False

    def removeResource(self, resourceName, amount):
        if amount >= 0 and resourceName in self._resources:
            resourceQueue = self._resources[resourceName]
            if not resourceQueue.tryPop(amount):
                return False
            if resourceQueue.isEmpty():
                self._resources.pop(resourceName)
            return True
        else:
            return False

    async def getStats(self, part=10):
        part, stats = self._toValidPart(part), []
        portfolioValue, _ = await self.portfolioValue(part)
        profits, _ = await self.getProfit(part, portfolioValue)
        nameToValue = {value.name: value for value in portfolioValue}
        nameToProfit = {profit.name: profit for profit in profits}

        for name in self._resources:
            resource = self._resources[name]
            if name in nameToValue:
                value = nameToValue[name]
            else:
                print(f"Error - Portfolio - getStats: no value for name: {name}")
                value = ResourceValue(name, 0, 0, 0, 0, 0)
            if name in nameToProfit:
                profit = nameToProfit[name]
            else:
                print(f"Error - Portfolio - getStats: no profit for name: {name}")
                profit = ResourceProfit(name, 0, 0, 0, 0)
            meanPurchase = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, resource.meanPurchase())
            meanPurchasePart = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, resource.meanPurchase(part))
            stats.append(ResourceStats(value, profit, meanPurchase, meanPurchasePart))

        return sorted(stats, key=lambda s: s.name), self._baseValue

    async def portfolioValue(self, part=10):
        part = self._toValidPart(part)
        valuesOfResources = []
        values = await asyncio.gather(*[self._valueService.getValue(resourceQueue, part) for resourceName, resourceQueue in self._resources.items()])
        for resourceName, resourceQueue in self._resources.items():
            fullValue, partValue = next(value[1] for value in values if value[0] == resourceName)
            fullValue = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, fullValue)
            partValue = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, partValue)
            recommendedApi, fullAmount = await self.getRecommendedApiForResource(resourceName), resourceQueue.amountLeft()

            valuesOfResources.append(ResourceValue(resourceName, fullAmount, fullValue, partValue, part, recommendedApi))
        return sorted(valuesOfResources, key=lambda val: val.name), self._baseValue

    async def getProfit(self, part=10, portfolioValue=None):
        part = self._toValidPart(part)
        if not portfolioValue:
            portfolioValue, _ = await self.portfolioValue(part)
        profits = []
        for resourceValue in portfolioValue:
            fullValue, partValue = resourceValue.fullValue, resourceValue.partValue
            fullAmount, partAmount = resourceValue.fullAmount, resourceValue.fullAmount / 100 * part

            meanPurchaseFull = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, self._resources[resourceValue.name].meanPurchase())
            meanPurchasePart = await self.cantorService.convertCurrencies(DEFAULT_VALUE, self._baseValue, self._resources[resourceValue.name].meanPurchase(part))

            fullProfit = (fullValue - meanPurchaseFull * fullAmount) * (1 - self._countryProfitFee)
            partProfit = (partValue - meanPurchasePart * partAmount) * (1 - self._countryProfitFee)
            profits.append(ResourceProfit(resourceValue.name, fullProfit, partProfit, fullAmount, part))
        return profits, self._baseValue

    async def getRecommendedApiForResource(self, resourceName, orderApiData=None):
        if not orderApiData:
            orderApiData = await self._valueService.getSorted(resourceName)
        if len(orderApiData):
            return orderApiData[0]['apiName']
        return 'Not Found'

    async def getAllArbitration(self, resource=None):
        if resource:
            resources = [resource]
        else:
            resources = [name for name in self._resources]
        resourcesProfits = []
        for resource in resources:
            services = await self.apiCrossProfitServices()
            profits = await ArbitrationService.getAllArbitration(resource, self._resources[resource].amountLeft(), services)
            for profit in profits:
                resourcesProfits.append(ResourceArbitration(
                    profit['currencies'][0], profit['currencies'][1], profit['names'][0], profit['names'][1], profit['rate'], profit['profit'], profit['quantity']))
        return sorted(resourcesProfits, key=lambda p: p.rate, reverse=True)

    async def apiCrossProfitServices(self):
        if not self._apiCrossProfitServices:
            self._apiCrossProfitServices = await ArbitrationService.getCrossArbitrationServices(self._apiList)
        return self._apiCrossProfitServices

    @staticmethod
    def _toValidPart(part):
        return max(0, min(100, part))
