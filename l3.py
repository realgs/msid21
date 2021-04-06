from enum import Enum

import requests

TRADE_MARKETS = ['bitbay', 'bittrex']
MARKETS_URL = ['https://bitbay.net/API/Public/', 'https://api.bittrex.com/v3/markets/']
TAKER_FEES = {
    'bitbay': 0.001,
    'bittrex': 0.0025
}
TRANSFER_FEES = {
    'bitbay': {
        'BTC': 0.0005,
        'LTC': 0.001,
        'ETH': 0.01,
        'DASH': 0.001
    },
    'bittrex': {
        'BTC': 0.0005,
        'LTC': 0.01,
        'ETH': 0.006,
        'DASH': 0.05
    }
}
CRYPTO_CURRENCIES = ['BTC', 'LTC', 'ETH', 'DASH']
BASE_CURRENCY = 'USD'


class Operations(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    ARB = 'ARBITRATION'


def getDataFromApi(url):
    response = requests.get(url)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        return None


def getSellBuyOffers(exchangeMarket, cypto, curency, offersLimit):
    if exchangeMarket == TRADE_MARKETS[0]:
        tradeOffers = getDataFromApi(MARKETS_URL[0] + cypto + curency + '/orderbook.json')
        offers = {'bids': tradeOffers['bids'][:offersLimit], 'asks': tradeOffers['asks'][:offersLimit]}
        if offers is not None:
            return offers
    elif exchangeMarket == TRADE_MARKETS[1]:
        tradeOffers = getDataFromApi(MARKETS_URL[1] + cypto + '-' + curency + '/orderbook')
        sellOffers = []
        buyOffers = []
        for bids in tradeOffers['bid'][:offersLimit]:
            buyOffers.append([float(bids['rate']), float(bids['quantity'])])
        for asks in tradeOffers['ask'][:offersLimit]:
            sellOffers.append([float(asks['rate']), float(asks['quantity'])])
        offers = {'bids': buyOffers, 'asks': sellOffers}
        if offers is not None:
            return offers
    return None


def findPriceDifferencesRatio(tradeOffer1, tradeOffer2):
    countTradeOffers1 = len(tradeOffer1)
    countTradeOffers2 = len(tradeOffer2)
    commonTradeOffersCount = min(countTradeOffers1, countTradeOffers2)
    differenceList = []
    for i in range(commonTradeOffersCount):
        difference = (1 - ((tradeOffer1[i][0] - tradeOffer2[i][0]) / (tradeOffer2[i][0]))) * 100
        differenceList.append(difference)

    return differenceList


def printDifferencesRatio(differences, crypto, currency, operation):
    print("Difference ratio in %: " + crypto + currency + ", for " + operation + " offers")
    for difference in differences:
        print(difference)


def printArbitrationDifferenceRatio(cheapestBuyOffer, expensiveSellOffer, differenceRatio):
    print("The cheapest buy offer on the first market: ", cheapestBuyOffer)
    print("The expensive sell offer on the second market: ", expensiveSellOffer)
    print("Arbitration difference ratio: ", differenceRatio)


def calculatePriceDifference(exchangeMarket: tuple, crypto, currency, offersLimit, delayOfExploringData, operation):
    tradeOffer1 = getSellBuyOffers(exchangeMarket[0], crypto, currency, offersLimit)
    tradeOffer2 = getSellBuyOffers(exchangeMarket[1], crypto, currency, offersLimit)
    buyOffers1 = tradeOffer1['bids']
    buyOffers2 = tradeOffer2['bids']
    sellOffers1 = tradeOffer1['asks']
    sellOffers2 = tradeOffer2['asks']
    print(tradeOffer1)
    print(tradeOffer2)
    if operation == Operations.BUY.value:
        differences = findPriceDifferencesRatio(buyOffers1, buyOffers2)
        printDifferencesRatio(differences, crypto, currency, operation)
    elif operation == Operations.SELL.value:
        differences = findPriceDifferencesRatio(sellOffers1, sellOffers2)
        printDifferencesRatio(differences, crypto, currency, operation)
    elif operation == Operations.ARB.value:
        sortedBuyOffers = sorted(buyOffers1, key=lambda x: x[0])
        theCheapestBuyOffer = sortedBuyOffers[0][0]
        reverseSortedSellOffers = sorted(sellOffers2, key=lambda x: x[0], reverse=True)
        theMostExpensiveSellOffer = reverseSortedSellOffers[0][0]
        differenceRatio = (1 - ((theMostExpensiveSellOffer - theCheapestBuyOffer) / (theCheapestBuyOffer))) * 100
        printArbitrationDifferenceRatio(theCheapestBuyOffer, theMostExpensiveSellOffer, differenceRatio)


calculatePriceDifference((TRADE_MARKETS[0], TRADE_MARKETS[1]), 'BTC', 'USD', 10, 0, 'ARBITRATION')
