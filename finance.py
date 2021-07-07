import time
from _datetime import datetime

SUCCESS_KEY = 'success'


class ProfitSeeker:
    def __init__(self, firstApi, secondApi):
        self.firstApi = firstApi
        self.secondApi = secondApi
        self.firstApiName = firstApi.getName()
        self.secondApiName = secondApi.getName()

    def _displayRate(self, firstApiData, secondApiData, source, message):
        firstApiBuy = firstApiData[source]['price']
        secondApiBuy = secondApiData[source]['price']
        rateFixed = "{:.6f}".format(firstApiBuy / secondApiBuy * 100)
        print(f"{message}: {self.firstApiName} / {self.secondApiName} = {rateFixed} %")

    def _displayBuyRate(self, firstApiData, secondApiData):
        self._displayRate(firstApiData, secondApiData, 'buy', 'Buy rate')

    def displayBuyRate(self, cryptos):
        bestFirst = self.firstApi.getBestOrders(cryptos)
        bestSecond = self.secondApi.getBestOrders(cryptos)

        if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
            self._displayBuyRate(bestFirst, bestSecond)
        else:
            print("The rate cannot be calculated")

    def _displaySellRate(self, firstApiData, secondApiData):
        self._displayRate(firstApiData, secondApiData, 'sell', 'Sell rate')

    def displaySellRate(self, cryptos):
        bestFirst = self.firstApi.getBestOrders(cryptos)
        bestSecond = self.secondApi.getBestOrders(cryptos)

        if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
            self._displayBuyRate(bestFirst, bestSecond)
        else:
            print("The rate cannot be calculated")

    def _getTransactionData(self, buyOrder, sellOrder, market1TakerFee, market2TakerFee, currency):
        rate = buyOrder['price'] * (1 - market1TakerFee) / sellOrder['price'] * (1 - market2TakerFee)
        quantity = min(buyOrder['quantity'], sellOrder['quantity'])
        priceDiffer = (rate - 1) * quantity
        profit = priceDiffer - self.firstApi.getTransferFee(currency) - self.secondApi.getTransferFee(currency)
        return rate, quantity, profit

    @staticmethod
    def _printFullInfo(buyIn, sellIn, rate, quantity, profit, currency):
        rateFixed = "{:.6f}".format(rate * 100)
        quantityFixed = "{:.6f}".format(quantity)
        if profit > 0:
            colorPrefix, colorSuffix = '\x1b[6;30;42m', '\x1b[0m'
        else:
            colorPrefix, colorSuffix = '\x1b[6;30;41m', '\x1b[0m'
        print(f"{colorPrefix}Buy in {buyIn}, sell in {sellIn}\t\tRate: {rateFixed},"
              f"\t\tQuantity: {quantityFixed},\t\tFull profit: {profit} {currency}{colorSuffix}")

    def _displayCrossProfitRate(self, firstApiData, secondApiData, currency):
        firstApiBuy, firstApiSell = firstApiData['buy'], firstApiData['sell']
        secondApiBuy, secondApiSell = secondApiData['buy'], secondApiData['sell']

        rate1, quantity1, profit1 = self._getTransactionData(firstApiBuy, secondApiSell, self.firstApi.getTakerFee(),
                                                             self.secondApi.getTakerFee(), currency)
        rate2, quantity2, profit2 = self._getTransactionData(secondApiBuy, firstApiSell, self.secondApi.getTakerFee(),
                                                             self.firstApi.getTakerFee(), currency)

        print("Profit percentage (100% - 0 profit):")
        self._printFullInfo(self.firstApiName, self.secondApiName, rate1, quantity1, profit1, currency)
        self._printFullInfo(self.secondApiName, self.firstApiName, rate2, quantity2, profit2, currency)

    def displayCrossProfitRate(self, cryptos):
        bestFirst = self.firstApi.getBestOrders(cryptos)
        bestSecond = self.secondApi.getBestOrders(cryptos)

        if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
            self._displayCrossProfitRate(bestFirst, bestSecond, cryptos[1])
        else:
            print("The profit rate cannot be calculated")

    def displayMarketsDifferenceRateStream(self, allCryptos, interval=5):
        while True:
            for cryptos in allCryptos:
                print("\n", datetime.now().strftime("%H:%M:%S"), f"{cryptos[0]} -> {cryptos[1]}")
                bestFirst = self.firstApi.getBestOrders(cryptos)
                bestSecond = self.secondApi.getBestOrders(cryptos)

                if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
                    self._displayBuyRate(bestFirst, bestSecond)
                    self._displaySellRate(bestFirst, bestSecond)
                    self._displayCrossProfitRate(bestFirst, bestSecond, cryptos[1])
                else:
                    print("The rate cannot be calculated")
                    return
            time.sleep(interval)
