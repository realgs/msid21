from services.connectionService import getApiResponse
from datetime import date

URL = 'http://api.nbp.pl/api/exchangerates/tables/a/last/1/?format=json'


class NBPCantorService:
    def __init__(self):
        self.lock = None
        self.dateRetrieved = None
        self.exchangeRates = []
        self.sync = ""

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
        else:
            print(f"Warning - NBPCantorService: cannot get exchange rate for value: {destinationCurrency}")
            return amount

    def _findCurrencyExchangeMid(self, currency):
        for exchangeData in self.exchangeRates:
            if exchangeData['code'] == currency:
                return exchangeData['mid']
        return None

    async def retrieveData(self):
        if not self.dateRetrieved or (date.today() - self.dateRetrieved).days > 1:
            apiResult = await getApiResponse(URL)
            if apiResult and len(apiResult):
                apiResult = apiResult[0]
                self._setDateRetrieved(apiResult['effectiveDate'])
                self.exchangeRates = apiResult['rates']
            else:
                print('Warning - NBPCantorService: cannot retrieve exchange rates')

    def _setDateRetrieved(self, dateString):
        year, month, day = dateString.split(sep='-')
        self.dateRetrieved = date(int(year), int(month), int(day))
