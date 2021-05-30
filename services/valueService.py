class ValueService:
    def __init__(self, defaultCurrency, apiList, successKey):
        self.defaultCurrency = defaultCurrency
        self.apiList = apiList
        self.successKey = successKey

    async def getValue(self, resource, part=10):
        buys = await self.getSortedOrders(resource.name)
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
            value += leftAmount * buys[-1]['order']['price']
        return value

    @staticmethod
    def _getOrderData(buys, idx, leftAmount):
        orderData = buys[idx]
        order = orderData['order']
        quantity = min(leftAmount, float(order['quantity']))
        return order, quantity

    async def getSortedOrders(self, resourceName):
        allOrders = [(await api['api'].getBestOrders((resourceName, self.defaultCurrency)), api['api'].getTakerFee(),
                      api['api'].getName()) for api in self.apiList]
        buys = []

        for orders, fee, apiName in allOrders:
            if orders[self.successKey]:
                for order in orders['buys']:
                    order['price'] = order['price'] * (1 - fee)
                    buys.append({'order': order, 'apiName': apiName})
        return sorted(buys, key=lambda buy: buy['order']['price'], reverse=True)
