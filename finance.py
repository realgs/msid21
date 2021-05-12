from _datetime import datetime
import asyncio
import time

SUCCESS_KEY = 'success'
ORDER_AMOUNT = 10
ACCURACY = 0.00000000001


class ProfitSeeker:
    def __init__(self, firstApi, secondApi):
        self.__firstApi = firstApi
        self.__secondApi = secondApi
        self.__commonMarkets = []

    async def _retrieveCommonAvailableMarkets(self):
        market1, market2 = await self.__firstApi.getAvailableMarkets(), await self.__secondApi.getAvailableMarkets()
        if not market1['success'] or not market2['success']:
            return []

        market1, market2 = market1['markets'], market2['markets']
        if len(market2) < len(market1):
            market2, market1 = market1, market2

        for market in market1:
            if any(m for m in market2 if m['currency1'] == market['currency1'] and m['currency2'] == market['currency2']):
                self.__commonMarkets.append(market)

    @property
    async def commonMarkets(self):
        if not self.__commonMarkets:
            await self._retrieveCommonAvailableMarkets()
        return self.__commonMarkets.copy()

    async def _getProfit(self, buyOrders, sellOrders, market1TakerFee, market2TakerFee, currency1, currency2):
        buyIdx, sellIdx = 0, 0
        fullQuantity, fullProfit, fullRate = 0, 0, 100
        canEarn = True

        while canEarn:
            quantity, profit, rate = self._getStats(buyOrders[buyIdx], sellOrders[sellIdx], market1TakerFee, market2TakerFee)
            self._updateQuantities(fullQuantity, profit, quantity, buyOrders[buyIdx], sellOrders[sellIdx])
            if fullQuantity < ACCURACY or profit > 0:
                fullProfit += profit
                fullQuantity += quantity

            if abs(buyOrders[buyIdx]['quantity']) < ACCURACY:
                buyIdx += 1
            else:
                sellIdx += 1
            canEarn = buyIdx < ORDER_AMOUNT and sellIdx < ORDER_AMOUNT and rate > 1

        transferFee1, transferFee2 = await self.__firstApi.getTransferFee(currency1), await self.__secondApi.getTransferFee(currency2)
        fullProfit = fullProfit - transferFee1 - transferFee2
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
    def _getStats(buyOrder, sellOrder, market1TakerFee, market2TakerFee):
        rate = buyOrder['price'] * (1 - market1TakerFee) / sellOrder['price'] * (1 - market2TakerFee)
        quantity = min(buyOrder['quantity'], sellOrder['quantity'])
        profit = (rate - 1) * quantity
        return quantity, profit, rate

    async def _getCrossProfitRate(self, firstApiData, secondApiData, currency1, currency2):
        firstApiBuy, firstApiSell = firstApiData['buys'], firstApiData['sells']
        secondApiBuy, secondApiSell = secondApiData['buys'], secondApiData['sells']

        quantity1, profit1 = await self._getProfit(firstApiBuy, secondApiSell, self.__firstApi.getTakerFee(),
                                                   self.__secondApi.getTakerFee(), currency1, currency2)
        quantity2, profit2 = await self._getProfit(secondApiBuy, firstApiSell, self.__secondApi.getTakerFee(),
                                                   self.__firstApi.getTakerFee(), currency2, currency1)

        return quantity1, profit1, profit1/quantity1, quantity2, profit2, profit2/quantity2

    @staticmethod
    def _printFullInfo(names, quantity, profit, currencies):
        quantityFixed = "{:.6f}".format(quantity)
        rate = profit / quantity
        if profit > 0:
            colorPrefix, colorSuffix = '\x1b[6;30;42m', '\x1b[0m'
        else:
            colorPrefix, colorSuffix = '\x1b[6;30;41m', '\x1b[0m'
        print(f"{colorPrefix}{currencies[0]} -> {currencies[1]},\t\tRate: {rate}%,\t\tFull profit: {profit} "
              f"{currencies[1]},\t\tBuy in {names[0]}, sell in {names[1]},\t\tQuantity: {quantityFixed} {currencies[1]}{colorSuffix}")

    async def displayAllPossibleProfits(self, interval=5):
        markets = await self.commonMarkets
        while True:
            startTime = datetime.now()
            orders = await asyncio.gather(*[self._retrieveOrders(market) for market in markets])
            orders = [o for o in orders if o[2]['success'] and o[3]['success']]

            marketsProfits = [await self._getTransferData(marketOrders) for marketOrders in orders]
            marketsProfits.sort(key=lambda profitData: profitData['rate'], reverse=True)

            endTime = datetime.now()
            delta = interval - (endTime - startTime).total_seconds()
            time.sleep(max(0.0, delta))
            print(f"\nBest profits: {datetime.now()}")
            for data in marketsProfits:
                self._printFullInfo(data['names'], data['quantity'], data['profit'], data['currencies'])

    async def _getTransferData(self, marketOrders):
        currency1, currency2, market1Data, market2Data = marketOrders
        quantity1, profit1, rate1, quantity2, profit2, rate2 = \
            await self._getCrossProfitRate(market1Data, market2Data, currency1, currency2)
        if profit1 > profit2:
            return {'rate': rate1, 'profit': profit1, 'quantity': quantity1, 'currencies': (currency1, currency2),
                    'names': (self.__firstApi.getName(), self.__secondApi.getName())}
        else:
            return {'rate': rate2, 'profit': profit2, 'quantity': quantity2, 'currencies': (currency2, currency1),
                    'names': (self.__secondApi.getName(), self.__firstApi.getName())}

    async def _retrieveOrders(self, markets):
        currency1, currency2 = markets['currency1'], markets['currency2']
        market1Data = await self.__firstApi.getBestOrders((currency1, currency2), ORDER_AMOUNT)
        market2Data = await self.__secondApi.getBestOrders((currency1, currency2), ORDER_AMOUNT)

        return currency1, currency2, market1Data, market2Data
