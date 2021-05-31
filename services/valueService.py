class ValueService:
    def __init__(self, defaultCurrency, apiList, successKey):
        self.defaultCurrency = defaultCurrency
        self.apiList = apiList
        self.successKey = successKey

    async def getValue(self, resource, part=10):
        buys = await self.getSorted(resource.name)
        fullAmount = resource.amountLeft()
        if not buys:
            return 0, 0
        else:
            return await self._calcValue(fullAmount, buys, part)

    async def _calcValue(self, fullAmount, buys, part):
        partValue = self._calcValueForAmount(buys, fullAmount / 100 * part)
        fullValue = self._calcValueForAmount(buys, fullAmount)
        return fullValue, partValue

    def _calcValueForAmount(self, buys, leftAmount):
        value = 0
        for idx in range(0, len(buys)):
            order, quantity = self._getOrderData(buys, idx, leftAmount)

            value += quantity * order['price']
            leftAmount -= quantity

            if leftAmount <= 0:
                break
        # We have more resources than api can offer
        if leftAmount > 0:
            value += leftAmount * buys[-1]['orderOrTicker']['price']
        return value

    @staticmethod
    def _getOrderData(buys, idx, leftAmount):
        orderData = buys[idx]
        order = orderData['orderOrTicker']
        quantity = min(leftAmount, float(order['quantity']))
        return order, quantity

    async def getSorted(self, resourceName):
        allOrders = [(await api['api'].orderbookOrTicker((resourceName, self.defaultCurrency)), api['api'].takerFee(),
                      api['api'].name()) for api in self.apiList]
        result = []

        for orderOrTicker, fee, apiName in allOrders:
            if orderOrTicker[self.successKey]:
                if 'orderbook' in orderOrTicker:
                    for order in orderOrTicker['orderbook']['buys']:
                        order['price'] = order['price'] * (1 - fee)
                        result.append({'orderOrTicker': order, 'apiName': apiName})
                else:
                    result.append({'orderOrTicker': orderOrTicker['ticker'], 'apiName': apiName})

        return sorted(result, key=lambda res: res['orderOrTicker']['price'], reverse=True)
