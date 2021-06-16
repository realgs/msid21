from API import const
from API.Api import Api, request
from API.NBP import NBP


class EOD(Api):
    def __init__(self):
        super().__init__("EOD", "https://eodhistoricaldata.com/api/real-time/")

    def markets(self):
        pass

    def orderbook(self, first, second):
        pass

    def transfer_fee(self, currency):
        pass

    def taker_fee(self):
        pass

    def get_price(self, stock_name, base_currency):
        json = request(f'{self.url}{stock_name}.WAR?api_token={const.EOD_TOKEN}&fmt=json')
        if json['high'] == 'NA' or json['low'] == 'NA':
            price = NBP().convert('PLN', json['previousClose'], base_currency)
        else:
            price = NBP().convert('PLN', (json['high'] + json['low']) / 2, base_currency)
        return price
