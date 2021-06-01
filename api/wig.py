from api.api import Api
from bs4 import BeautifulSoup
import requests

NAME = "WIG"
DEFAULT_TRANSFER_FEE = 0
URL = "https://www.bankier.pl/gielda/notowania/akcje"
STATUS_OK = "Ok"
STATUS_KEY = "status"
BASE_VALUE = "PLN"


class Wig(Api):
    def __init__(self, cantorService):
        super().__init__(NAME)
        self._available = set()
        self._cantorService = cantorService

    async def transferFee(self, resource):
        return DEFAULT_TRANSFER_FEE

    async def orderbookOrTicker(self, resources, amount=None):
        resource, currency = resources
        if resource in await self.availableMarkets:
            html_content = requests.get(URL).text
            soup = BeautifulSoup(html_content, "html.parser")
            foundTr = soup.find_all('tr')
            for idx in range(1, len(foundTr)):
                data = foundTr[idx].text.split()
                if len(data) > 1 and data[0] == resource:
                    price = float(data[1].replace(',', '.'))
                    price = await self._cantorService.convertCurrencies(BASE_VALUE, currency, price)
                    return {"success": True, "ticker": {'price': price, 'quantity': 0}}
        return {"success": False, "cause": f"Cannot retrieve data fot resource: {resource}"}

    @property
    async def availableMarkets(self):
        if not self._available:
            html_content = requests.get(URL).text
            soup = BeautifulSoup(html_content, "html.parser")
            foundTr = soup.find_all('tr')
            for idx in range(1, len(foundTr)):
                data = foundTr[idx].text.split()
                if len(data) > 1:
                    self._available.add(data[0])
        return self._available

    async def available(self):
        data = await self.availableMarkets
        if data:
            markets = [{'currency1': market, 'currency2': BASE_VALUE} for market in data]
            return {"success": True, 'markets': markets}
        return {"success": False, "cause": "Cannot retrieve data"}
