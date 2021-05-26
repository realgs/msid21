from APIs.API import API


class MarketStackAPI(API):
    BASEURL = 'http://api.marketstack.com/v1/'
    KEY = 'f789505bd3e8854c80a555bb8b9d5f24'
    TAKER_FEE = 0.0043  # percentage

    def get_intraday(self, symbol):
        query = self.BASEURL + "intraday?access_key=" + self.KEY + "&symbols=" + symbol
        response = super(MarketStackAPI, self).query(query)
        if response.status_code == 200:
            return response.json()

    def get_last_transaction(self, symbol):
        intraday = self.get_intraday(symbol)
        if intraday is None:
            return None
        return intraday.get('data')[0]
