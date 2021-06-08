from api.api import Api, TYPE_CURRENCY

NAME = "NBP Web Api"
BASE_VALUE = "PLN"


class Nbp(Api):
    def __init__(self, cantorService):
        super().__init__(NAME, TYPE_CURRENCY)
        self.cantorService = cantorService

    async def orderbookOrTicker(self, resources, amount=None):
        currency1, currency2 = resources
        markets = await self.cantorService.getAvailableCurrency()
        if currency1 not in markets or currency2 not in markets:
            return {"success": False, "cause": f"Not supported resource: {currency1}, {currency2}"}

        result = await self.cantorService.convertCurrencies(currency1, currency2, 1)
        return {"success": True, "ticker": {'price': result, 'quantity': 0}}

    async def available(self):
        data = sorted(await self.cantorService.getAvailableCurrency())
        if data:
            markets = [{'currency1': market, 'currency2': BASE_VALUE} for market in data]
            return {"success": True, 'markets': markets}
        return {"success": False, "cause": "Cannot retrieve data"}
