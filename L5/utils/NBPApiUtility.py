import utils.ApiUtility as ApiUtility


class NBPApiUtility(ApiUtility.ApiUtility):

    def __init__(self):
        super().__init__("NBP", "http://api.nbp.pl/api/exchangerates/rates")

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

    def get_ticker(self, symbol_from, symbol_to, quantity):
        if symbol_from == symbol_to:
            return quantity
        if symbol_from == 'PLN':
            url = f"{self._api_url}/c/{symbol_to}/"
            response = self.request_to_api(url)
            return quantity / float(response['rates'][0]['ask'])
        elif symbol_to == 'PLN':
            url = f"{self._api_url}/c/{symbol_from}/"
            response = self.request_to_api(url)
            return quantity * float(response['rates'][0]['bid'])

        conv_value = self.get_ticker(symbol_from, 'PLN', quantity)
        return self.get_ticker('PLN', symbol_to, conv_value)
