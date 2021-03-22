import requests


class Offer:
    def __init__(self, market, transaction_type, quantity, rate):
        self.market = market
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.rate = rate

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.rate}'


def get_orderlist(markets):
    offers = []
    for market in markets:
        market_json = requests.get('https://api.bittrex.com/api/v1.1/public/getorderbook?',
                                           {'market': market, 'type': 'both'}).json()['result']
        for transaction_type in ['buy', 'sell']:
            for offer in market_json['buy']:
                offers.append(Offer(market=market, transaction_type=transaction_type, quantity=offer['Quantity'],
                                    rate=offer['Rate']))

    return offers


def print_orderlist(orderlist):
    for order in orderlist:
        print(order)


market_list = ['USD-BTC', 'USD-LTC', 'USD-ETH']
order_list = get_orderlist(market_list)
print_orderlist(order_list)
