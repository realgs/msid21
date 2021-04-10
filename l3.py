from enum import Enum
from time import sleep
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
DELAY_OF_EXPLORING_DATA = 5
DATA_LIMIT = 10


class Operation(Enum):
    BUY = "BUY"
    SELL = "SELL"
    ARBITRATION = "ARBITRATION"
    ARBITRATION_EXTENDED = "ARBITRATION WITH FEES"


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


def printArbitrationTransactionInfo(exchangeMarket: tuple, cheapestBuyOffer, expensiveSellOffer, differenceRatio,
                                    volume=0, realTransactionVolume=0, profitPercentage=0, profit=0,
                                    operation=Operation.ARBITRATION.value):

    print("Info for: ", operation)
    print("The cheapest buy offer on: " + exchangeMarket[0] + " is: ", cheapestBuyOffer)
    print("The most expensive sell offer on: " + exchangeMarket[1] + ' is: ', expensiveSellOffer)
    print("Arbitration difference ratio ", differenceRatio, '%')
    print("Transaction volume: ", volume)
    print("Transaction volume after calculated fees: ", realTransactionVolume)
    print("Profit percentage: ", profitPercentage, '%')
    print("Potential profit of arbitration transaction: ", profit, 'USD')


def calculateArbitrageDifferenceRatio(theCheapestBuyOffer, theMostExpensiveSellOffer):
    differenceRatio = (1 - ((theMostExpensiveSellOffer - theCheapestBuyOffer) / theCheapestBuyOffer)) * 100
    return differenceRatio


def calculateTransactionVolumeAfterFees(exchangeMarket: tuple, transactionVolume, crypto):
    buyTakerFee = 0
    sellTakerFee = 0
    transferFee = 0

    if exchangeMarket[0] == TRADE_MARKETS[0]:
        buyTakerFee = TAKER_FEES['bitbay']
        transferFee = TRANSFER_FEES['bitbay'][crypto]
        sellTakerFee = TAKER_FEES['bittrex']
    elif exchangeMarket[0] == TRADE_MARKETS[1]:
        buyTakerFee = TAKER_FEES['bittrex']
        transferFee = TRANSFER_FEES['bittrex'][crypto]
        sellTakerFee = TAKER_FEES['bitbay']

    buyFee = transactionVolume * buyTakerFee
    sellFee = transactionVolume * sellTakerFee
    fee = buyFee + sellFee + transferFee
    transactionVolume = transactionVolume - fee
    return transactionVolume


def calculateArbitrageProfit(realTransactionVolume, theCheapestBuyOffer, theMostExpensiveSellOffer):
    difference = theMostExpensiveSellOffer - theCheapestBuyOffer
    profit = difference * realTransactionVolume
    return profit


def calculatePriceDifferences(exchangeMarket: tuple, crypto, currency, offersLimit, delayOfExploringData):
    while True:
        tradeOffer1 = getSellBuyOffers(exchangeMarket[0], crypto, currency, offersLimit)
        tradeOffer2 = getSellBuyOffers(exchangeMarket[1], crypto, currency, offersLimit)
        print(tradeOffer1)
        print(tradeOffer2)
        buyOffers1 = tradeOffer1['bids']
        buyOffers2 = tradeOffer2['bids']
        sellOffers1 = tradeOffer1['asks']
        sellOffers2 = tradeOffer2['asks']
        # buy operation
        differences = findPriceDifferencesRatio(buyOffers1, buyOffers2)
        printDifferencesRatio(differences, crypto, currency, Operation.BUY.value)

        # sell operation
        differences = findPriceDifferencesRatio(sellOffers1, sellOffers2)
        printDifferencesRatio(differences, crypto, currency, Operation.SELL.value)

        # arbitration and extended arbitration
        sortedBuyOffers = sorted(buyOffers1, key=lambda x: x[0])
        theCheapestBuyOffer = sortedBuyOffers[0][0]
        reverseSortedSellOffers = sorted(sellOffers2, key=lambda x: x[0], reverse=True)
        theMostExpensiveSellOffer = reverseSortedSellOffers[0][0]
        differenceRatio = calculateArbitrageDifferenceRatio(theCheapestBuyOffer, theMostExpensiveSellOffer)

        # arbitration without fees
        printArbitrationTransactionInfo(exchangeMarket, theCheapestBuyOffer, theMostExpensiveSellOffer,
                                        differenceRatio)

        # arbitration with fees
        transactionVolume = min(sortedBuyOffers[0][1], reverseSortedSellOffers[0][1])
        realTransactionVolume = calculateTransactionVolumeAfterFees(exchangeMarket, transactionVolume, crypto)
        profit = calculateArbitrageProfit(realTransactionVolume, theCheapestBuyOffer, theMostExpensiveSellOffer)
        profitPercentage = (profit / (theMostExpensiveSellOffer * realTransactionVolume)) * 100
        printArbitrationTransactionInfo(exchangeMarket, theCheapestBuyOffer, theMostExpensiveSellOffer, differenceRatio,
                                        transactionVolume, realTransactionVolume, profitPercentage, profit,
                                        Operation.ARBITRATION_EXTENDED.value)

        sleep(delayOfExploringData)


def main():
    calculatePriceDifferences((TRADE_MARKETS[0], TRADE_MARKETS[1]), 'BTC', BASE_CURRENCY, DATA_LIMIT, DELAY_OF_EXPLORING_DATA)


if __name__ == '__main__':
    main()
