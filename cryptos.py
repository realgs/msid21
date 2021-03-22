import time

import requests


class Offer:
    def __init__(self, market, transaction_type, quantity, price):
        self.market = market
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.price}'


def get_offerlist(markets):
    offers = []
    for market in markets:
        market_json = requests.get('https://api.bittrex.com/api/v1.1/public/getorderbook?',
                                           {'market': market, 'type': 'both'}).json()['result']
        for transaction_type in ['buy', 'sell']:
            for offer in market_json[transaction_type]:
                offers.append(Offer(market=market, transaction_type=transaction_type, quantity=offer['Quantity'],
                                    price=offer['Rate']))

    return offers


def print_list(ls):
    for item in ls:
        print(item)


def count_ratios(markets, offers):
    res_list = []
    for market_name in markets:
        temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers))
        buy_offer_list = list(filter(lambda offer: offer.transaction_type == 'buy', temp_offer_list))
        sell_offer_list = list(filter(lambda offer: offer.transaction_type == 'sell', temp_offer_list))
        counts_number = len(buy_offer_list) if len(buy_offer_list) <= len(sell_offer_list) else sell_offer_list
        for i in range(counts_number):
            result = 1 - (sell_offer_list[i].price - buy_offer_list[i].price) / buy_offer_list[i].price
            res_list.append(f'{market_name} buy - sell ratio: ' + '{:.1f}%'.format(result*100) +
                            f' for sell price {sell_offer_list[i].price} and buy price {buy_offer_list[i].price}')

    return res_list


def get_datastream(markets):
    while True:
        offers = get_offerlist(markets)
        print_list(offers)
        print('\n')
        ratios = count_ratios(markets, offers)
        print_list(ratios)
        print('\n')
        time.sleep(5)
