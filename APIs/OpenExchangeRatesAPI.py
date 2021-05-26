from APIs.API import API


class OpenExchangeRatesAPI(API):
    BASEURL = 'https://openexchangerates.org/api/'
    APP_ID = '2267072d16484231ab35bb33e6000e1e'

    def get_latest_rates(self, base_currency):
        if base_currency != 'USD':
            print("To query other base currencies than USD you have to upgrade your OpenExchangeRates account")
            return None

        query = self.BASEURL + "latest.json?app_id=" + self.APP_ID + "&base=" + base_currency
        response = super(OpenExchangeRatesAPI, self).query(query)
        if response.status_code == 200:
            return response.json()

    def get_latest_currency_pair(self, base_currency, currency):
        latest_currencies = self.get_latest_rates(base_currency)
        if latest_currencies is None:
            return None
        return latest_currencies.get('rates')[currency]
