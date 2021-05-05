import json

from arbitrage import findArbitages, getTransferFees, getMarketsNames, printArbitrages, \
    collectOffers, findMarketsIntersection
from constants import APIS


def loadDataFromFile(path: str):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
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


