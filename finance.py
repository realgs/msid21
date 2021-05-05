import time
from _datetime import datetime

SUCCESS_KEY = 'success'
ORDER_AMOUNT = 10
ACCURACY = 0.00000000001


class ProfitSeeker:
    def __init__(self, firstApi, secondApi):
        self.__firstApi = firstApi
        self.__secondApi = secondApi
        self.__commonMarkets = []
        self.retrieveCommonAvailableMarkets()

    def retrieveCommonAvailableMarkets(self):
        firstApiMarkets = self.__firstApi.getAvailableMarkets()
        secondApiMarkets = self.__secondApi.getAvailableMarkets()
        if not firstApiMarkets['success'] or not secondApiMarkets['success']:
            return None

        firstApiMarkets = firstApiMarkets['markets']
        secondApiMarkets = secondApiMarkets['markets']
        if len(secondApiMarkets) < len(firstApiMarkets):
            secondApiMarkets, firstApiMarkets = firstApiMarkets, secondApiMarkets

        for market in firstApiMarkets:
            if any(m for m in secondApiMarkets if m['currency1'] == market['currency1'] and m['currency2'] == market['currency2']):
                self.__commonMarkets.append({'data': market, 'reverse': False})
            elif any(m for m in secondApiMarkets if m['currency2'] == market['currency1'] and m['currency1'] == market['currency2']):
                self.commonMarkets.append({'data': market, 'reverse': True})

    @property
    def commonMarkets(self):
        return [m['data'] for m in self.__commonMarkets]

    def _displayRate(self, firstApiData, secondApiData, source, message):
        firstApiBuy = firstApiData[source][0]['price']
        secondApiBuy = secondApiData[source][0]['price']
        rateFixed = "{:.6f}".format(firstApiBuy / secondApiBuy * 100)
        print(f"{message}: {self.__firstApi.getName()} / {self.__secondApi.getName()} = {rateFixed} %")

    def _displayBuyRate(self, firstApiData, secondApiData):
        self._displayRate(firstApiData, secondApiData, 'buys', 'Buy rate')

    def displayBuyRate(self, cryptos):
        bestFirst = self.__firstApi.getBestOrders(cryptos)
        bestSecond = self.__secondApi.getBestOrders(cryptos)

        if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
            self._displayBuyRate(bestFirst, bestSecond)
        else:
            print("The rate cannot be calculated")

    def _displaySellRate(self, firstApiData, secondApiData):
        self._displayRate(firstApiData, secondApiData, 'sells', 'Sell rate')

    def displaySellRate(self, cryptos):
        bestFirst = self.__firstApi.getBestOrders(cryptos)
        bestSecond = self.__secondApi.getBestOrders(cryptos)

        if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
            self._displayBuyRate(bestFirst, bestSecond)
        else:
            print("The rate cannot be calculated")

    def _getProfit(self, buyOrders, sellOrders, market1TakerFee, market2TakerFee, currency1, currency2):
        buyIdx, sellIdx = 0, 0
        fullQuantity, fullProfit = 0, 0
        canEarn = True

        while buyIdx < ORDER_AMOUNT and sellIdx < ORDER_AMOUNT and canEarn:
            quantity, profit = self._getTransactionData(buyOrders[buyIdx], sellOrders[sellIdx], market1TakerFee, market2TakerFee)

            self._updateQuantities(fullQuantity, profit, quantity, buyOrders[buyIdx], sellOrders[sellIdx])
            if fullQuantity < ACCURACY or profit > 0:
                fullProfit += profit
                fullQuantity += quantity
            if abs(buyOrders[buyIdx]['quantity']) < ACCURACY:
                buyIdx += 1
            else:
                sellIdx += 1
            canEarn = buyOrders[buyIdx]['price'] / sellOrders[sellIdx]['price'] > 1

        print("profit przed:", fullProfit)
        fullProfit = fullProfit - self.__firstApi.getTransferFee(currency1) - self.__secondApi.getTransferFee(currency2)
        print("profit po:", fullProfit)
        return fullQuantity, fullProfit

    @staticmethod
    def _updateQuantities(fullQuantity, profit, quantity, buyOrder, sellOrder):
        if fullQuantity < ACCURACY or profit > 0:
            buyOrder['quantity'] -= quantity
            sellOrder['quantity'] -= quantity
        else:
            if buyOrder['quantity'] > sellOrder['quantity']:
                sellOrder['quantity'] -= quantity
            else:
                buyOrder['quantity'] -= quantity


    @staticmethod
    def _getTransactionData(buyOrder, sellOrder, market1TakerFee, market2TakerFee):
        rate = buyOrder['price'] * (1 - market1TakerFee) / sellOrder['price'] * (1 - market2TakerFee)
        quantity = min(buyOrder['quantity'], sellOrder['quantity'])
        profit = (rate - 1) * quantity
        return quantity, profit

    @staticmethod
    def _printFullInfo(buyIn, sellIn, quantity, profit, currencySource, currencyTarget):
        quantityFixed = "{:.6f}".format(quantity)
        if profit > 0:
            colorPrefix, colorSuffix = '\x1b[6;30;42m', '\x1b[0m'
        else:
            colorPrefix, colorSuffix = '\x1b[6;30;41m', '\x1b[0m'
        #TODO: profit from currencyTarget to USD
        print(f"{colorPrefix}Buy in {buyIn}, sell in {sellIn}\t\t{currencySource} -> {currencyTarget},\t\t"
              f"Quantity: {quantityFixed},\t\tFull profit: {profit} USD{colorSuffix}")

    def _displayCrossProfitRate(self, firstApiData, secondApiData, currency1, currency2):
        firstApiBuy, firstApiSell = firstApiData['buys'], firstApiData['sells']
        secondApiBuy, secondApiSell = secondApiData['buys'], secondApiData['sells']

        quantity1, profit1 = self._getProfit(firstApiBuy, secondApiSell, self.__firstApi.getTakerFee(),
                                             self.__secondApi.getTakerFee(), currency1, currency2)
        quantity2, profit2 = self._getProfit(secondApiBuy, firstApiSell, self.__secondApi.getTakerFee(),
                                             self.__firstApi.getTakerFee(), currency2, currency1)

        print("Profit percentage (100% - 0 profit):")
        self._printFullInfo(self.__firstApi.getName(), self.__secondApi.getName(), quantity1, profit1, currency1, currency2)
        self._printFullInfo(self.__secondApi.getName(), self.__firstApi.getName(), quantity2, profit2, currency2, currency1)

    def displayCrossProfitRate(self, allCryptos):
        for cryptos in allCryptos:
            bestFirst = self.__firstApi.getBestOrders(cryptos, ORDER_AMOUNT)
            bestSecond = self.__secondApi.getBestOrders(cryptos, ORDER_AMOUNT)

            if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
                self._displayCrossProfitRate(bestFirst, bestSecond, cryptos[0], cryptos[1])
            else:
                print("The profit rate cannot be calculated")

    def displayAllPossibleProfits(self):
        # TODO: While loop
        marketsProfits = []
        for markets in self.__commonMarkets:
            currency1, currency2 = markets['data']['currency1'], markets['data']['currency2']
            bestMarket1 = self.__firstApi.getBestOrders((currency2, currency1), ORDER_AMOUNT)

            if not markets['reverse']:
                bestMarket2 = self.__secondApi.getBestOrders((currency2, currency1), ORDER_AMOUNT)
            else:
                bestMarket2 = self.__secondApi.getBestOrders((currency1, currency2), ORDER_AMOUNT)

            firstApiBuy, firstApiSell = bestMarket1['buys'], bestMarket1['sells']
            secondApiBuy, secondApiSell = bestMarket2['buys'], bestMarket2['sells']
            quantity1, profit1 = self._getProfit(firstApiBuy, secondApiSell, self.__firstApi.getTakerFee(),
                                                 self.__secondApi.getTakerFee(), currency1, currency2)
            quantity2, profit2 = self._getProfit(secondApiBuy, firstApiSell, self.__secondApi.getTakerFee(),
                                                 self.__firstApi.getTakerFee(), currency2, currency1)
            if profit1 > profit2:
                marketsProfits.append((profit1, quantity1, currency1, currency2, self.__firstApi.getName(), self.__secondApi.getName()))
            else:
                marketsProfits.append((profit2, quantity2, currency2, currency1, self.__secondApi.getName(), self.__firstApi.getName()))
        marketsProfits.sort(key=lambda data: data[0], reverse=True)
        for data in marketsProfits:
            self._printFullInfo(data[4], data[5], data[1], data[0], data[2], data[3])

    def displayMarketsDifferenceRateStream(self, allCryptos, interval=5):
        while True:
            for cryptos in allCryptos:
                print("\n", datetime.now().strftime("%H:%M:%S"), f"{cryptos[0]} -> {cryptos[1]}")
                bestFirst = self.__firstApi.getBestOrders(cryptos, ORDER_AMOUNT)
                bestSecond = self.__secondApi.getBestOrders(cryptos, ORDER_AMOUNT)

                if bestFirst[SUCCESS_KEY] and bestSecond[SUCCESS_KEY]:
                    self._displayBuyRate(bestFirst, bestSecond)
                    self._displaySellRate(bestFirst, bestSecond)
                    self._displayCrossProfitRate(bestFirst, bestSecond, cryptos[0], cryptos[1])
                else:
                    print("The rate cannot be calculated")
                    return
            time.sleep(interval)
