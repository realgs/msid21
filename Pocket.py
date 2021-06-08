import BitBay
import BitTrex
import Currencies
import PolishStocks
import USAstocks
import json

SERVICES = {'Crypto': [BitBay.BitBay(), BitTrex.BitTrex()], 'PL': [PolishStocks.Bankier()], 'USA':[USAstocks.Yahoo()],
            'Curr': [Currencies.NBP()]}
NETTO = 0.19
DEFAULT_DEPTH = 15

def loadPortfolio():
    data = open('resources.json')
    return json.load(data)

def prepareData(percent):
    data = loadPortfolio()

    result = []

    for element in data:
        resource = {}

        resource['name'] = element['symbol']

        resource['ammount'] = element['ammount']

        resource['currency'] = element['currency']

        maxLastPrice = 0
        for api in SERVICES[element['market']]:
            maxLastPrice = max(maxLastPrice, api.lastMaxPrice(resource['name'], baseCurrency=element['currency']))
        resource['lastTransactionPrice'] = maxLastPrice

        maxValue = 0
        sellIn = ''
        for api in SERVICES[element['market']]:
            newValue = api.sell(resource['name'], resource['ammount'], element['currency'])
            if ( newValue > maxValue ):
                maxValue = newValue
                sellIn = api.getName()
        resource['value'] = maxValue

        maxValue = 0
        for api in SERVICES[element['market']]:
            maxValue = max(maxValue, api.sell(resource['name'], percent * resource['ammount'], element['currency']))
        resource['percentValue'] = maxValue

        profit = resource['value'] - ( element['averagePrice'] * element['ammount'] )
        if (profit > 0 ):
            payments = profit * NETTO
        else:
            payments = 0
        resource['netto'] = round(resource['value']-payments, 2)

        profit = resource['percentValue'] - (element['averagePrice'] * element['ammount'])
        if (profit > 0):
            payments = profit * NETTO
        else:
            payments = 0
        resource['percentNetto'] = round(resource['percentValue'] - payments, 2)

        resource['sellIn'] = sellIn

        resource['arbitrageOptions'] = arbitrage(element['market'], resource['name'])
        #if ( resource['arbitrageOptions'][1] == 0 ):
            #resource['arbitrageOptions'] = 'No abailable options'

        result.append(resource)

    return result

def printInfo(info):
    for i in info:
        print(i)


def arbitrage(market, resource):
    options = []
    for api in SERVICES[market]:
        sellTable = api.getResourceBidAskTable(resource)
        for api2 in SERVICES[market]:
            buyTable = api.getResourceBidAskTable(resource)

            profit = calculateProfit(sellTable, buyTable)
            options.append([api.getName() + ' -> ' + api2.getName(), profit])

    options = sorted(options, key=(lambda element: element[1]), reverse=True)
    return options[0]

def calculateProfit(sellTable, buyTable):
    bidDepth = 0
    askDepth = 0
    profit = 0

    while (bidDepth < len(sellTable) and askDepth < len(buyTable)):
        if ( sellTable['bid'][bidDepth][0] > buyTable['ask'][askDepth][0]):
            ammountToTransfer = min(sellTable['bid'][bidDepth][1], buyTable['ask'][askDepth][1])
            sellTable['bid'][bidDepth][1] -= ammountToTransfer
            buyTable['ask'][askDepth][1] -= ammountToTransfer
            profit += (sellTable['bid'][bidDepth][0] - buyTable['ask'][askDepth][0]) * ammountToTransfer

            if ( sellTable['bid'][bidDepth][1] == 0):
                bidDepth += 1
            if ( buyTable['ask'][askDepth][1] == 0):
                askDepth += 1

        else:
            return round(profit, 2)
