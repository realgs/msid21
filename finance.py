from _datetime import datetime

SUCCESS_KEY = 'success'
ORDER_AMOUNT = 10
ACCURACY = 0.00000000001


class ProfitSeeker:
    def __init__(self, firstApi, secondApi):
        self.__firstApi = firstApi
        self.__secondApi = secondApi
        self.__commonMarkets = []
        self._retrieveCommonAvailableMarkets()

    def _retrieveCommonAvailableMarkets(self):
        firstApiMarkets = self.__firstApi.getAvailableMarkets()
        secondApiMarkets = self.__secondApi.getAvailableMarkets()
        if not firstApiMarkets['success'] or not secondApiMarkets['success']:
            return None

        firstApiMarkets = firstApiMarkets['markets']
        secondApiMarkets = secondApiMarkets['markets']
        if len(secondApiMarkets) < len(firstApiMarkets):
            secondApiMarkets, firstApiMarkets = firstApiMarkets, secondApiMarkets

        for market in firstApiMarkets:
            if any(m for m in secondApiMarkets if
                   m['currency1'] == market['currency1'] and m['currency2'] == market['currency2']):
                self.__commonMarkets.append({'data': market, 'reverse': False})
            elif any(m for m in secondApiMarkets if
                     m['currency2'] == market['currency1'] and m['currency1'] == market['currency2']):
                self.commonMarkets.append({'data': market, 'reverse': True})

    @property
    def commonMarkets(self):
        return [m['data'] for m in self.__commonMarkets]

    def _getProfit(self, buyOrders, sellOrders, market1TakerFee, market2TakerFee, currency1, currency2):
        buyIdx, sellIdx = 0, 0
        fullQuantity, fullProfit, fullRate = 0, 0, 100
        canEarn = True

        while canEarn:
            quantity, profit, rate = self._getTransactionStats(buyOrders[buyIdx], sellOrders[sellIdx], market1TakerFee, market2TakerFee)
            self._updateQuantities(fullQuantity, profit, quantity, buyOrders[buyIdx], sellOrders[sellIdx])
            if fullQuantity < ACCURACY or profit > 0:
                fullProfit += profit
                fullQuantity += quantity

            if abs(buyOrders[buyIdx]['quantity']) < ACCURACY:
                buyIdx += 1
            else:
                sellIdx += 1
            canEarn = buyIdx > ORDER_AMOUNT and sellIdx > ORDER_AMOUNT and rate > 1

        fullProfit = fullProfit - self.__firstApi.getTransferFee(currency1) - self.__secondApi.getTransferFee(currency2)
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
    def _getTransactionStats(buyOrder, sellOrder, market1TakerFee, market2TakerFee):
        rate = buyOrder['price'] * (1 - market1TakerFee) / sellOrder['price'] * (1 - market2TakerFee)
        quantity = min(buyOrder['quantity'], sellOrder['quantity'])
        profit = (rate - 1) * quantity
        return quantity, profit, rate

    def _getCrossProfitRate(self, firstApiData, secondApiData, currency1, currency2):
        firstApiBuy, firstApiSell = firstApiData['buys'], firstApiData['sells']
        secondApiBuy, secondApiSell = secondApiData['buys'], secondApiData['sells']

        quantity1, profit1 = self._getProfit(firstApiBuy, secondApiSell, self.__firstApi.getTakerFee(), self.__secondApi.getTakerFee(), currency1, currency2)
        quantity2, profit2 = self._getProfit(secondApiBuy, firstApiSell, self.__secondApi.getTakerFee(), self.__firstApi.getTakerFee(), currency2, currency1)

        return quantity1, profit1, profit1 / quantity1, quantity2, profit2, profit2 / quantity2

    @staticmethod
    def _printFullInfo(names, quantity, profit, currencies):
        quantityFixed = "{:.6f}".format(quantity)
        rate = profit / quantity
        if profit > 0:
            colorPrefix, colorSuffix = '\x1b[6;30;42m', '\x1b[0m'
        else:
            colorPrefix, colorSuffix = '\x1b[6;30;41m', '\x1b[0m'
        print(f"{colorPrefix}{currencies[0]} -> {currencies[1]},\t\tRate: {rate}%,\t\tFull profit: {profit} "
              f"{currencies[1]},\t\tBuy in {names[0]}, sell in {names[1]},\t\tQuantity: {quantityFixed}{colorSuffix}")

    def displayAllPossibleProfits(self):
        while True:
            marketsProfits = []
            print(f'<{"-"* (len(self.commonMarkets)-2)}>')

            for markets in self.__commonMarkets:
                marketsProfits.append(self._getMarketsTransferData(markets))
                print('#', end='')

            marketsProfits.sort(key=lambda profitData: profitData['rate'], reverse=True)
            print(f"\nBest profits: {datetime.now()}")
            for data in marketsProfits:
                self._printFullInfo(data['names'], data['quantity'], data['profit'], data['currencies'])

    def _getMarketsTransferData(self, markets):
        currency1, currency2 = markets['data']['currency1'], markets['data']['currency2']
        market1Data, market2Data = self._retrieveMarketOrders(currency1, currency2, markets['reverse'])
        quantity1, profit1, rate1, quantity2, profit2, rate2 = self._getCrossProfitRate(market1Data, market2Data,currency1, currency2)
        if profit1 > profit2:
            return {'rate': rate1, 'profit': profit1, 'quantity': quantity1, 'currencies': (currency1, currency2),
                    'names': (self.__firstApi.getName(), self.__secondApi.getName())}
        else:
            return {'rate': rate2, 'profit': profit2, 'quantity': quantity2, 'currencies': (currency2, currency1),
                    'names': (self.__secondApi.getName(), self.__firstApi.getName())}

    def _retrieveMarketOrders(self, currency1, currency2, reverse):
        market1Data = self.__firstApi.getBestOrders((currency2, currency1), ORDER_AMOUNT)

        if not reverse:
            market2Data = self.__secondApi.getBestOrders((currency2, currency1), ORDER_AMOUNT)
        else:
            market2Data = self.__secondApi.getBestOrders((currency1, currency2), ORDER_AMOUNT)
        return market1Data, market2Data
