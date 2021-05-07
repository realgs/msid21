import json
import asyncio

from arbitrage import findArbitages, getTransferFees, getMarketsNames, printArbitrages, \
    collectOffers, findMarketsIntersection, collectOffersAsync
from constants import APIS


def loadDataFromFile(path: str):
    with open(path) as f:
        return json.load(f)


def runProgram():
    exchangeMarkets = ("bittrex", "bitbay")
    APIS[exchangeMarkets[0]]["transferFee"] = getTransferFees(exchangeMarkets[0])
    markets1 = getMarketsNames(exchangeMarkets[0])
    markets2 = getMarketsNames(exchangeMarkets[1])

    intersectionMarkets = sorted(findMarketsIntersection(markets1, markets2))

    # allOffers = loadDataFromFile('./data.json')
    allOffers = collectOffers(list(APIS.keys()), intersectionMarkets)
    arbitrages1 = findArbitages(exchangeMarkets, allOffers)
    arbitrages2 = findArbitages(exchangeMarkets[::-1], allOffers)
    printArbitrages(arbitrages1, arbitrages2, 100)


def runProgram2():
    exchangeMarkets = ("bittrex", "bitbay")
    APIS[exchangeMarkets[0]]["transferFee"] = getTransferFees(exchangeMarkets[0])
    markets1 = getMarketsNames(exchangeMarkets[0])
    markets2 = getMarketsNames(exchangeMarkets[1])

    intersectionMarkets = sorted(findMarketsIntersection(markets1, markets2))
    allOffers = asyncio.run(collectOffersAsync(list(APIS.keys()), intersectionMarkets))
    arbitrages1 = findArbitages(exchangeMarkets, allOffers)
    arbitrages2 = findArbitages(exchangeMarkets[::-1], allOffers)
    printArbitrages(arbitrages1, arbitrages2, 100)


if __name__ == "__main__":
    runProgram2()
