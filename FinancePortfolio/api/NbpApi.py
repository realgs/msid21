from FinancePortfolio.api.Api import Api, API_TYPES

NAME = 'Narodowy Bank Polski'
SHORT_NAME = 'NBP'
BASE_URL = 'http://api.nbp.pl/api/exchangerates/rates/'


class NbpApi(Api):

    def __init__(self):
        super().__init__(
            name=NAME,
            short_name=SHORT_NAME,
            base_url=BASE_URL,
            api_type=API_TYPES[2]
        )

    def convertCurrency(self, currency_from, currency_to, amount):
        if currency_from == currency_to:
            return amount
        elif currency_from == 'PLN':
            url = f'{self.baseUrl}c/{currency_to}/'
            response = self.getApiResponse(url)
            return amount / float(response['rates'][0]['ask'])
        elif currency_to == 'PLN':
            url = f'{self.baseUrl}c/{currency_from}/'
            response = self.getApiResponse(url)
            return amount * float(response['rates'][0]['bid'])
        else:
            result = self.convertCurrency(currency_from, 'PLN', amount)
            return self.convertCurrency('PLN', currency_to, result)
