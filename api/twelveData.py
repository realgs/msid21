from api.api import Api
from services.connectionService import getApiResponse
import credentials

NAME = "TwelveData"
TAKER_FEE = 0  # TODO: Set fees
DEFAULT_TRANSFER_FEE = 0
API_BASE_URL = "https://twelve-data1.p.rapidapi.com/"
BASE_VALUE = "USD"
STATUS_KEY = 'status'
STATUS_ERR = 'error'
X_RAPIDAPI_HOST = 'twelve-data1.p.rapidapi.com'


class TwelveData(Api):
    def __init__(self, cantorService):
        super().__init__(NAME, TAKER_FEE)
        self.cantorService = cantorService
        self.headers = {'x-rapidapi-key': credentials.X_RAPIDAPI_KEY, 'x-rapidapi-host': X_RAPIDAPI_HOST}

    async def getTransferFee(self, resource):
        return DEFAULT_TRANSFER_FEE

    async def getBestOrders(self, resources, amount=None):
        symbol, currency = resources
        apiResult = await getApiResponse(f"{API_BASE_URL}price?symbol={symbol}&format=json&outputsize=30",
                                         headers=self.headers)
        if apiResult is None:
            return {"success": False, "cause": f"To many calls for api {self.getName()}"}
        if apiResult is not None and STATUS_KEY not in apiResult or apiResult[STATUS_KEY] != STATUS_ERR:
            price = await self.cantorService.convertCurrencies(BASE_VALUE, currency, float(apiResult['price']))
            value = [{"price": price, 'quantity': 0}]
            return {"success": True, "buys": value, "sells": value}
        return {"success": False, "cause": f"Cannot retrieve data fot resource: {symbol} or numer of calls exceeded"}

    async def getAvailableMarkets(self):
        apiResult = await getApiResponse(f"{API_BASE_URL}stocks?exchange=NASDAQ&format=json", headers=self.headers)
        if STATUS_KEY not in apiResult or apiResult[STATUS_KEY] != STATUS_ERR:
            markets = []
            for marketData in apiResult['data']:
                markets.append({'currency1': marketData['symbol'], 'currency2': BASE_VALUE})
            return {"success": True, 'markets': markets}
        return {"success": False, "cause": "Cannot retrieve data"}
