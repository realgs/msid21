import itertools
from dataclasses import dataclass

PRINT_ROW_FORMAT = "{} -> {}, MARKET: {}, QUANTITY: {}, PROFIT: {}, PRICE: {}"
PRINT_ARBITRATIONS_IS_NONE = "Arbitrations is None"


@dataclass
class _ArbitrageResult:
    buyFrom: str
    sellTo: str
    market: (str, str)
    quantity: float = 0
    price: float = 0
    profit: float = 0


class ArbitrationProcessor:
    def __init__(self, dataProvider):
        self.dataProvider = dataProvider
        self.commonMarkets = set()

    def prepareCommonMarkets(self):
        self.apiNames = self.dataProvider.getRegisteredApiNames()

        commonMarkets = self.dataProvider.fetchNormalizedMarkets(
            self.apiNames[0])
        for name in self.apiNames[1:]:
            markets = self.dataProvider.fetchNormalizedMarkets(name)
            commonMarkets = commonMarkets.intersection(markets)

        self.commonMarkets = commonMarkets

    def __fetchAllOrderBooks(self):
        data = dict()

        for name in self.apiNames:
            data[name] = dict()
            for market in self.commonMarkets:
                data[name][market] = self.dataProvider.fetchNormalizedOrderBook(
                    name, market)
        return data

    def __calculateArbitration(self, buyFromApiOffers, sellToApiOffers, market):
        buyOffersIndex = 0
        sellOffersIndex = 0

        sellOffers = buyFromApiOffers.sellOffers
        buyOffers = sellToApiOffers.buyOffers

        isWorth = buyOffers[buyOffersIndex].price > sellOffers[sellOffersIndex].price

        if not isWorth:
            return _ArbitrageResult(
                buyFromApiOffers.owner.name,
                sellToApiOffers.owner.name,
                market=market
            )

        canStillBeBought = float(sellOffers[sellOffersIndex].amount)
        canStillBeSold = float(buyOffers[buyOffersIndex].amount)
        overallBuyPrice = buyFromApiOffers.owner.getWithdrawalFee(market)
        overallSellPrice = sellToApiOffers.owner.getDepositFee(market)
        overallQuantity = 0

        while buyOffersIndex < len(buyOffers) and sellOffersIndex < len(sellOffers) and isWorth:
            maxTransfered = min(canStillBeBought, canStillBeSold)
            buyPrice = maxTransfered * float(sellOffers[sellOffersIndex].price)
            buyPrice += buyPrice * buyFromApiOffers.owner.takerFee

            sellPrice = maxTransfered * float(buyOffers[buyOffersIndex].price)
            sellPrice += sellPrice * sellToApiOffers.owner.takerFee

            isWorth = overallSellPrice + sellPrice > overallBuyPrice + buyPrice
            if isWorth:
                overallBuyPrice += buyPrice
                overallSellPrice += sellPrice
                overallQuantity += maxTransfered

                canStillBeBought -= maxTransfered
                canStillBeSold -= maxTransfered

                if canStillBeSold == 0:
                    buyOffersIndex += 1
                    canStillBeSold = float(buyOffers[buyOffersIndex].amount)
                if canStillBeBought == 0:
                    sellOffersIndex += 1
                    canStillBeBought = float(
                        sellOffers[sellOffersIndex].amount)
                isWorth = buyOffers[buyOffersIndex].price > sellOffers[sellOffersIndex].price

        return _ArbitrageResult(
            buyFromApiOffers.owner.name,
            sellToApiOffers.owner.name,
            market,
            overallQuantity,
            overallBuyPrice,
            overallSellPrice - overallBuyPrice
        )

    def createArbitrationsList(self):
        combinations = list(itertools.combinations(self.apiNames, 2))
        data = self.__fetchAllOrderBooks()
        arbitrations = list()

        for comparison in combinations:
            stApi = data[comparison[0]]
            ndApi = data[comparison[1]]
            for market in self.commonMarkets:
                arbitrations.append(self.__calculateArbitration(
                    stApi[market], ndApi[market], market))
                arbitrations.append(self.__calculateArbitration(
                    ndApi[market], stApi[market], market))

        return arbitrations

    def printArbitrationsRank(self, arbitrations):
        if arbitrations is not None:
            copy = arbitrations.copy()
            copy.sort(reverse=True, key=lambda value: value.profit)
            for arbitration in copy:
                print(PRINT_ROW_FORMAT.format(arbitration.buyFrom,
                                              arbitration.sellTo,
                                              arbitration.market,
                                              arbitration.quantity,
                                              arbitration.profit,
                                              arbitration.price
                                              ))
        else:
            print(PRINT_ARBITRATIONS_IS_NONE)
