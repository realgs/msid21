from services.configurationService import readConfig, saveConfig
from models.resource import Resource
from services.converter import convertCurrencies

FILENAME = 'portfolio_data.json'


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
            pass
        else:
            self._resources[resource.name] = resource

    def save(self):
        data = {'baseValue': self._baseValue, 'resources': [resource.toDict() for _,resource in self._resources.items()]}
        saveConfig(self._owner+"_"+FILENAME, data)
