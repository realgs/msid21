from services.configurationService import readConfig, saveConfig
from models.resource import Resource, ResourceValue
from services.converter import convertCurrencies
from api import bitbay, bittrex
import asyncio

FILENAME = 'portfolio_data.json'
API_LIST = [bitbay, bittrex]

class Portfolio:
    def __init__(self, owner, baseValue):
        self._owner = owner
        self._baseValue = baseValue
        self._resources = {}

    def read(self):
        data = readConfig(self._owner+"_"+FILENAME)
        if data:
            self._resources = {resource['name']: Resource.fromDict(resource) for resource in data['resources']}
            if self._baseValue != data['baseValue']:
                for resource in self._resources.values():
                    resource.meanPurchase = convertCurrencies(data['baseValue'], self._baseValue, resource.meanPurchase)
            return True
        else:
            return False

    def addResource(self, resource):
        if resource.name in self._resources:
            self._resources[resource.name].add(resource)
        else:
            self._resources[resource.name] = resource

    async def getFullPortfolioValue(self):
        return await self.portfolioValue(100)

    async def portfolioValue(self, part):
        valuesOfResources = []
        for resource in self._resources:
            allOrders = await asyncio.gather(*[(api.getBestOrders((self._baseValue, resource.name)), api.getTakerFee()) for api in API_LIST])
            # TODO: sprawdz czy dobra kolumna
            sellFees = [(orderList['sells'], takerFee) for orderList, takerFee in allOrders if orderList['success']]
            sellFees = sorted(sellFees, key=lambda order: order[0]['price'], reverse=True)
            name, amount, meanPurchase = resource.name, resource.amount * part / 100, resource.meanPurchase
            if not sellFees:
                valuesOfResources.append(ResourceValue(name, amount, meanPurchase, 0))
            else:
                amount = resource.amount
                fullValue = 0

                for sells, fee in sellFees:
                    quantity = min(amount, sells['quantity'])
                    fullValue += quantity * sells['price'] * (1 - fee)
                    amount -= quantity
                    if amount <= 0:
                        break

                if amount > 0:
                    fullValue += amount * (sellFees[-1][0]['price'] * (1 - sellFees[-1][1]))

                valuesOfResources.append(ResourceValue(name, amount, meanPurchase, fullValue))
        # TODO: Return in readable form

    def save(self):
        data = {'baseValue': self._baseValue, 'resources': [resource.toDict() for _,resource in self._resources.items()]}
        saveConfig(self._owner+"_"+FILENAME, data)
