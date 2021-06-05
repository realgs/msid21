import BitBay
import BitTrex
import CurrencyChange
import PolishStocks
import USAstocks
import json

SERVICES = {'Crypto': [BitBay, BitTrex], 'Currency': [CurrencyChange], 'PL': [PolishStocks], 'USA':[USAstocks] }
NETTO = 0.81

def loadPortfolio():
    data = open('resources.json')
    return json.load(data)

def prepareData(percent=0.1):
    data = loadPortfolio()

    result = []

    for element in data:
        resource = {}

        resource['name'] = element['symbol']

        resource['ammount'] = element['ammount']

        resource['average'] = element['averagePrice']

        value = 0
        for market in SERVICES[element['market']]:
            newValue = market.value(element['symbol'], element['ammount'], element['currency'])
            if ( newValue > value):
                resource['value'] = round(newValue, 2)
                value = newValue
                resource['market'] = market.name()

        partValue = 0
        for market in SERVICES[element['market']]:
            partNewValue = market.value(element['symbol'], percent * element['ammount'], element['currency'])
            if (partNewValue > partValue):
                resource['partValue'] = round(partNewValue, 2)
                partValue = partNewValue
                resource['partMarket'] = market.name()

        resource['netto'] = round(NETTO * resource['value'], 2)
        resource['partNetto'] = round(NETTO * resource['partValue'], 2)

        resource['arbitrage'] = arbitrage(element['market'], element['symbol'], element['ammount'],
                                          element['currency'] ,resource['value'] )

        result.append(resource)

    for i in result:
        print(i)

def arbitrage(market, resource, ammount, baseCurrency, value):
    options = []
    for element in SERVICES[market]:
        buyFor = element.buy(resource, ammount, baseCurrency)
        if ( buyFor is not None and buyFor < value ):
            options.append([buyFor, element.name()])

    if (len(options) is 0):
        return None
    else:
        options = sorted(options, key=(lambda element: element[0]), reverse=True)
        return options[0]


if __name__ == "__main__":
    prepareData(0.01)
