import utils.ApiUtility as ApiUtility
import utils.EOD_API_KEY as PRIVATE_API_KEY
import utils.NBPApiUtility as NBPUtility



class EODApiUtility(ApiUtility.ApiUtility):

    def __init__(self):
        super().__init__("EOD", "https://eodhistoricaldata.com/api/real-time/")

    def get_taker_fee(self):
        raise NotImplementedError()

    def get_transfer_fee(self, symbol):
        raise NotImplementedError()

    def get_markets(self):
        raise NotImplementedError()

    def if_orderbook_supported(self):
        return False

    def get_orderbook(self, symbol):
        raise NotImplementedError()

    def get_ticker(self, symbol, base_currency):
        response = self.request_to_api(f'{self._api_url}{symbol}.WAR?api_token={PRIVATE_API_KEY.PRIVATE_API_KEY}&fmt=json')
        if response['high'] == 'NA' or response['low'] == 'NA':
            return NBPUtility.NBPApiUtility().get_ticker('PLN', base_currency, response['previousClose'])
        else:
            return NBPUtility.NBPApiUtility().get_ticker('PLN', base_currency, (response['high'] + response['low']) / 2)
