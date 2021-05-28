from API.Api import request, Api


class NBP(Api):
    def __init__(self):
        super().__init__('NBP', 'http://api.nbp.pl/api/exchangerates/rates/c/')

    def markets(self):
        pass

    def orderbook(self, first, second):
        pass

    def transfer_fee(self, currency):
        pass

    def taker_fee(self):
        pass

    def convert(self, cur_from: str, quantity: float, cur_to: str):
        if cur_from == cur_to:
            return quantity
        if cur_from == 'PLN':
            json = request(f'{self.url}{cur_to}')
            return quantity / float(json['rates'][0]['ask'])
        elif cur_to == 'PLN':
            json = request(f'{self.url}' + f'{cur_from}')
            return quantity * float(json['rates'][0]['bid'])

        conv_value = self.convert(cur_from, quantity, 'PLN')
        return self.convert('PLN', conv_value, cur_to)
