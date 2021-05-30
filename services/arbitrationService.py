import asyncio

SUCCESS_KEY = 'success'
ORDER_AMOUNT = 10
ACCURACY = 0.00000000001


class ArbitrationService:
    def __init__(self, firstApi, secondApi):
        self.__firstApi = firstApi
        self.__secondApi = secondApi
        self.__commonMarkets = []

    async def _retrieveCommonAvailableMarkets(self):
        market1, market2 = await self.__firstApi.getAvailableMarkets(), await self.__secondApi.getAvailableMarkets()
        if not market1['success'] or not market2['success']:
            return None

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
    async def getAllArbitration(resourceName1, resourceAmount1, resourceName2, resourceAmount2, arbitrationServices):
        allProfits = []
        for profitService in arbitrationServices:
            # data = await profitService.getPossibleArbitration({'currency1': resourceName1, 'currency2': resourceName2}, True)
            data = await profitService.getPossibleArbitration({'currency1': resourceName1, 'currency2': resourceName2})
            if data and len(data):
                allProfits.append(data[0])
        allProfits = sorted(allProfits, key=lambda data: data['rate'], reverse=True)
        return ArbitrationService._getPossibleProfits(allProfits, resourceAmount1, resourceAmount2)

    @staticmethod
    def _getPossibleProfits(allProfits, resourceAmount1, resourceAmount2):
        amount = min(resourceAmount1, resourceAmount2)
        bestArbitration = []
        for profit in allProfits:
            quantity = min(amount, profit['quantity'])
            profit['quantity'] = quantity
            bestArbitration.append(profit)
            amount -= quantity
            if amount < 0:
                break
        return bestArbitration

    @staticmethod
    async def getCrossArbitrationServices(apiList):
        crossArbitrationServices = []
        for idx1 in range(0, len(apiList)):
            api1 = apiList[idx1]
            for idx2 in range(idx1 + 1, len(apiList)):
                api2 = apiList[idx2]
                if api1['type'] == api2['type']:
                    profitService = ArbitrationService(api1['api'], api2['api'])
                    commonMarkets = await profitService.commonMarkets
                    if commonMarkets:
                        crossArbitrationServices.append(profitService)
        return crossArbitrationServices

    async def getPossibleArbitration(self, clientMarkets, onlyProfits=False):
        allMarkets = await self.commonMarkets
        markets = [markets for markets in allMarkets if markets['currency1'] == clientMarkets['currency1'] and markets['currency2'] == clientMarkets['currency2']]

        orders = await asyncio.gather(*[self._retrieveOrders(market) for market in markets])
        orders = [o for o in orders if o[2]['success'] and o[3]['success']]

        marketsProfits = [await self._getTransferData(marketOrders) for marketOrders in orders]
        if onlyProfits:
            marketsProfits = [marketsProfit for marketsProfit in marketsProfits if marketsProfit['rate'] > 0]

        marketsProfits.sort(key=lambda profitData: profitData['rate'], reverse=True)
        return marketsProfits

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
