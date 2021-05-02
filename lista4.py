from math import fabs
from time import sleep

import requests

BITTREX_MARKET_URL = 'https://api.bittrex.com/v3/markets/'
BITBAY_MARKET_URL = 'https://api.bitbay.net/rest/trading/ticker'
DEFAULT_SEARCHING_DEPTH = 5
EXTENDED_SEARCHING_DEPTH = 20
TIME_TO_SLEEP = 10

EXAMPLE_RESOURCES = ['BTC-USD', 'ETH-USD', 'LTC-USD']

BITTREX_ORDER_URL = 'https://api.bittrex.com/v3/markets/'
BITTREX_ORDER_URL_2 = '/orderbook'
BITTREX_TAKER_FEE = 0.0035

BITBAY_ORDER_URL = 'https://bitbay.net/API/Public/'
BITBAY_ORDER_URL_2 = '/orderbook.json'
BITBAY_TAKER_FEE = 0.0042

# returns list resources on Bittrex
def getBittrexMarket():
    result = []
    bittrexDownload = requests.get(BITTREX_MARKET_URL)

    if (bittrexDownload.status_code == 200):
        bittrexJson = bittrexDownload.json()

        for element in range(0, len(bittrexJson)):
            result.append(bittrexJson[element]['symbol'])

    return result

# returns list resources on Bitbay
def getBitbayMarket():
    result = []
    bitbayDownload = requests.get(BITBAY_MARKET_URL)

    if (bitbayDownload.status_code == 200):
        bitbayJson = bitbayDownload.json()
        bitbayItems = bitbayJson['items']
        bitbayKeys = bitbayItems.keys()

        for element in bitbayKeys:
            result.append(element)

    return result

# returns list of usable resources
def getCommonMarket(market1, market2):
    result = []
    for element in market1:
        if (market2.__contains__(element)):
            result.append(element)

    result.sort()

    return result

# returns list of common base currencies
def getBaseCurrencies(data):
    dict = {}

    for element in data:
        splited = element.split('-')
        dict[splited[1]] = 'newOne'

    return list(dict.keys())

# leaves resources with given base currency
def dataFilter(data, filtr):
    result = []
    for element in data:
        splited = element.split('-')
        if (splited[1] == filtr):
            result.append(element)

    return result

#-----------------------------------------------------------------------------------------------------------------------

# returns dict with offers for resource
def getOffers(resource, depth=DEFAULT_SEARCHING_DEPTH):
    result = {'resource': resource, 'bittrex': {}, 'bitbay': {}}


    result['bittrex']['bidPrice'] = []
    result['bittrex']['bidAmmount'] = []
    result['bittrex']['askPrice'] = []
    result['bittrex']['askAmmount'] = []

    bittrexDownload = requests.get(BITTREX_ORDER_URL + resource + BITTREX_ORDER_URL_2)
    if (bittrexDownload.status_code == 200):

        bittrexJson = bittrexDownload.json()

        try:
            for i in range(depth):
                result['bittrex']['bidPrice'].append(float(bittrexJson['bid'][i]['rate']))
            for i in range(depth):
                result['bittrex']['bidAmmount'].append(float(bittrexJson['bid'][i]['quantity']))
            for i in range(depth):
                result['bittrex']['askPrice'].append(float(bittrexJson['ask'][i]['rate']))
            for i in range(depth):
                result['bittrex']['askAmmount'].append(float(bittrexJson['ask'][i]['quantity']))
        except:
            return None




    result['bitbay']['bidPrice'] = []
    result['bitbay']['bidAmmount'] = []
    result['bitbay']['askPrice'] = []
    result['bitbay']['askAmmount'] = []

    bitbayDownload = requests.get(BITBAY_ORDER_URL + resource.replace('-', '') + BITBAY_ORDER_URL_2)
    if (bitbayDownload.status_code == 200):

        bitbayJson = bitbayDownload.json()

        try:
            for i in range(depth):
                result['bitbay']['bidPrice'].append(bitbayJson['bids'][i][0])
            for i in range(depth):
                result['bitbay']['bidAmmount'].append(bitbayJson['bids'][i][1])
            for i in range(depth):
                result['bitbay']['askPrice'].append(bitbayJson['asks'][i][0])
            for i in range(depth):
                result['bitbay']['askAmmount'].append(bitbayJson['asks'][i][1])
        except:
            return None


    return result


def calculateProfit(resourceInfo, bittrexToBitbay=True, feeIncluded=False):
    bidDepth = 0
    askDepth = 0
    taken = 0
    profit = 0

    if (bittrexToBitbay):
        while (bidDepth < DEFAULT_SEARCHING_DEPTH and askDepth < DEFAULT_SEARCHING_DEPTH):
            ammountToTransfer = min(resourceInfo['bittrex']['askAmmount'][askDepth], resourceInfo['bitbay']['bidAmmount'][bidDepth])
            taken += ammountToTransfer
            priceDifferencial = resourceInfo['bitbay']['bidPrice'][bidDepth] - resourceInfo['bittrex']['askPrice'][askDepth]


            # return loss if no ability to trade
            if (priceDifferencial <= 0 and askDepth == 0 and bidDepth == 0):
                profit = priceDifferencial * ammountToTransfer
                if ( feeIncluded ):
                    profit -= fabs( profit * BITTREX_TAKER_FEE)
                return profit

            # return profit if there is ability to earn money
            if (priceDifferencial <= 0):
                if ( feeIncluded ):
                    profit -= fabs( profit * BITTREX_TAKER_FEE)
                return profit

            resourceInfo['bittrex']['askAmmount'][askDepth] -= ammountToTransfer
            resourceInfo['bitbay']['bidAmmount'][bidDepth] -= ammountToTransfer

            if (resourceInfo['bittrex']['askAmmount'][askDepth] == 0):
                askDepth += 1
            if (resourceInfo['bitbay']['bidAmmount'][bidDepth] == 0):
                bidDepth += 1

            profit += priceDifferencial * ammountToTransfer

        if (askDepth > 10):
            if (feeIncluded):
                profit -= fabs(profit * BITTREX_TAKER_FEE)
            return profit

        return calculateProfit(getOffers(resourceInfo['resource'], EXTENDED_SEARCHING_DEPTH), bittrexToBitbay)

    else:
        while (bidDepth < DEFAULT_SEARCHING_DEPTH and askDepth < DEFAULT_SEARCHING_DEPTH):
            ammountToTransfer = min(resourceInfo['bitbay']['askAmmount'][askDepth], resourceInfo['bittrex']['bidAmmount'][bidDepth])
            priceDifferencial = resourceInfo['bittrex']['bidPrice'][bidDepth] - resourceInfo['bitbay']['askPrice'][askDepth]


            # return loss if no ability to trade
            if (priceDifferencial <= 0 and askDepth == 0 and bidDepth == 0):
                profit = priceDifferencial * ammountToTransfer
                if ( feeIncluded ):
                    profit -= fabs( profit * BITBAY_TAKER_FEE)
                return profit

            # return profit if there is ability to earn money
            if (priceDifferencial <= 0):
                if ( feeIncluded ):
                    profit -= fabs( profit * BITBAY_TAKER_FEE)
                return profit

            resourceInfo['bitbay']['askAmmount'][askDepth] -= ammountToTransfer
            resourceInfo['bittrex']['bidAmmount'][bidDepth] -= ammountToTransfer

            if (resourceInfo['bitbay']['askAmmount'][askDepth] == 0):
                askDepth += 1
            if (resourceInfo['bittrex']['bidAmmount'][bidDepth] == 0):
                bidDepth += 1

            profit += priceDifferencial * ammountToTransfer

        if (askDepth > 10):
            if (feeIncluded):
                profit -= fabs(profit * BITBAY_TAKER_FEE)
            return profit

        return calculateProfit(getOffers(resourceInfo['resource'], EXTENDED_SEARCHING_DEPTH), bittrexToBitbay)


# returns list of resources
def prepareStatement(data, feeIncluded=False):
    result = []
    for element in data:
        elementOffer = getOffers(element)

        bitbaytoBittrexProfit = calculateProfit(elementOffer, False, feeIncluded)
        bittrexToBitbayProfit = calculateProfit(elementOffer, True, feeIncluded)
        if ( bitbaytoBittrexProfit > bittrexToBitbayProfit ):
            direction = 'bitbayToBittrex'
            profit = bitbaytoBittrexProfit
        else:
            direction = 'bittrexToBitbay'
            profit = bittrexToBitbayProfit

        result.append([profit, elementOffer['resource'], direction])

    return result



def sortStatement(statement):
    for i in range(len(statement)):
        for j in range(len(statement)-1):
            if (statement[j][0] < statement[j+1][0]):
                k = statement[j]
                statement[j] = statement[j+1]
                statement[j+1] = k

    return statement



def printStatement(statement):
    number = 1
    for element in statement:
        splited = element[1].split('-')
        if ( element[0] >= 0 ):
            sign = '+'
        else:
            sign = ''

        print(str(number) + ') ' + sign + str(element[0]) + ' ' + splited[1] + '   (' + element[1] + ') ' + element[2])
        number += 1

    print('\n\n')



def printExample():
    print('Example:')
    selected = EXAMPLE_RESOURCES
    statement = prepareStatement(selected, False)
    statement = sortStatement(statement)
    printStatement(statement)

    

if __name__ == '__main__':
    # ex1
    commonMarket = (getCommonMarket(getBitbayMarket(), getBittrexMarket()))
    baseCurrencies = getBaseCurrencies(commonMarket)
    
    
    # ex2
    printExample()
    
    
    # ex3
    while ( True ):

        for currency in baseCurrencies:
            selected = dataFilter(commonMarket, currency)
            statement = prepareStatement(selected, False)
            statement = sortStatement(statement)
            printStatement(statement)

            sleep(TIME_TO_SLEEP)
