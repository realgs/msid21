from services.connectionService import getApiResponse
from datetime import date

URL = 'http://api.nbp.pl/api/exchangerates/tables/a/last/1/?format=json'


class NBPCantorService:
    def __init__(self):
        self.dateRetrieved = None
        self.exchangeRates = {'PLN': 1}

    async def convertCurrencies(self, sourceCurrency, destinationCurrency, amount):
        await self.retrieveData()
        if sourceCurrency != 'PLN':
            plnRate = self._findCurrencyExchangeMid(sourceCurrency)
            if plnRate is None:
                print(f"Warning - NBPCantorService: cannot get exchange rate for value: {sourceCurrency}")
                plnRate = 1
            amount = amount * plnRate

        if destinationCurrency == 'PLN':
            exchangeRate = 1
        else:
            exchangeRate = self._findCurrencyExchangeMid(destinationCurrency)
        if exchangeRate:
            return amount / exchangeRate
        print(f"Warning - NBPCantorService: cannot get exchange rate for value: {destinationCurrency}")
        return amount

    async def getAvailableCurrency(self):
        await self.retrieveData()
        return [code for code in self.exchangeRates]

    def _findCurrencyExchangeMid(self, currency):
        if currency in self.exchangeRates:
            return self.exchangeRates[currency]
        return None

    async def retrieveData(self):
        if not self.dateRetrieved or (date.today() - self.dateRetrieved).days > 1:
            apiResult = await getApiResponse(URL)
            if apiResult and len(apiResult):
                apiResult = apiResult[0]
                self._setDateRetrieved(apiResult['effectiveDate'])
                self.exchangeRates = {rate['code']: rate['mid'] for rate in apiResult['rates']}
                self.exchangeRates['PLN'] = 1
            else:
                print('Warning - NBPCantorService: cannot retrieve exchange rates')

    def _setDateRetrieved(self, dateString):
        year, month, day = dateString.split(sep='-')
        self.dateRetrieved = date(int(year), int(month), int(day))
