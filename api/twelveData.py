from api.api import Api
from services.connectionService import getApiResponse
from configurations import credentials

NAME = "TwelveData"
API_BASE_URL = "https://twelve-data1.p.rapidapi.com/"
BASE_VALUE = "USD"
STATUS_KEY = 'status'
STATUS_ERR = 'error'
X_RAPIDAPI_HOST = 'twelve-data1.p.rapidapi.com'


class TwelveData(Api):
    def __init__(self, cantorService):
        super().__init__(NAME)
        self.cantorService = cantorService
        self._headers = {'x-rapidapi-key': credentials.X_RAPIDAPI_KEY, 'x-rapidapi-host': X_RAPIDAPI_HOST}
        self._availableMarkets = set()

    @property
    async def availableMarkets(self):
        if not self._availableMarkets:
            apiResult = await getApiResponse(f"{API_BASE_URL}stocks?exchange=NASDAQ&format=json", headers=self._headers)
            if STATUS_KEY not in apiResult or apiResult[STATUS_KEY] != STATUS_ERR:
                self._availableMarkets = [marketData['symbol'] for marketData in apiResult['data']]
        return self._availableMarkets

    async def orderbookOrTicker(self, resources, amount=None):
        symbol, currency = resources
        if symbol not in await self.availableMarkets:
            return {"success": False, "cause": f"Cannot retrieve data fot resource: {symbol}"}

        apiResult = await getApiResponse(f"{API_BASE_URL}price?symbol={symbol}&format=json&outputsize=30", headers=self._headers)
        if apiResult is not None and (STATUS_KEY not in apiResult or apiResult[STATUS_KEY] != STATUS_ERR):
            price = await self.cantorService.convertCurrencies(BASE_VALUE, currency, float(apiResult['price']))
            return {"success": True, "ticker": {'price': price, 'quantity': 0}}
        return {"success": False, "cause": f"Cannot retrieve data fot resource: {symbol} or to many calls for api {self.name()}"}

    async def available(self):
        data = await self.availableMarkets
        if data:
            markets = [{'currency1': market, 'currency2': BASE_VALUE} for market in data]
            return {"success": True, 'markets': markets}
        return {"success": False, "cause": "Cannot retrieve data"}
