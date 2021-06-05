import BitBay
import BitTrex
import CurrencyChange
import PolishStocks
import USAstocks
import json

SERVICES = {'Crypto': [BitBay.BitBay(), BitTrex.BitTrex()], 'PL': [PolishStocks.Bankier()], 'USA':[USAstocks.Yahoo()]}
NETTO = 0.81

def loadPortfolio():
    data = open('resources.json')
    return json.load(data)

def prepareData():
    data = loadPortfolio()

    result = []
    percent = int(input("Enter percent to sell: "))
    percent /= 100

    for element in data:
        resource = {}

        resource['name'] = element['symbol']

        resource['ammount'] = element['ammount']

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
        resource['sellIn'] = sellIn

        maxValue = 0
        for api in SERVICES[element['market']]:
            maxValue = max(maxValue, api.sell(resource['name'], percent * resource['ammount'], element['currency']))
        resource['percentValue'] = maxValue

        profit = resource['value'] - ( element['averagePrice'] * element['ammount'] )
        if (profit > 0 ):
            resource['netto'] = round( NETTO * profit, 2 )
        else:
            resource['netto'] = round( profit, 2 )

        profit = resource['percentValue'] - (element['averagePrice'] * percent * element['ammount'])
        if (profit > 0):
            resource['percentNetto'] = round(NETTO * profit, 2)
        else:
            resource['percentNetto'] = round(profit, 2)

        print(resource)



