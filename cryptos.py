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
        market_json = requests.get(f'https://api.bittrex.com/v3/markets/{market}/orderbook?depth=25').json()
        for transaction_type in ['bid', 'ask']:
            for offer_json in market_json[transaction_type]:
                offers.append(Offer(market=market, transaction_type=transaction_type,
                                    quantity=float(offer_json['quantity']), price=float(offer_json['rate'])))

    return offers


def print_list(ls):
    for item in ls:
        print(item)


def count_ratios(markets, offers):
    res_list = []
    for market_name in markets:
        temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers))
        bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))
        ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))
        counts_number = len(bid_offer_list)
        for i in range(counts_number):
            result = 1 - (ask_offer_list[i].price - bid_offer_list[i].price) / bid_offer_list[i].price
            res_list.append(f'{market_name} buy - sell ratio: ' + '{:.1f}%'.format(result * 100) +
                            f' for sell price {ask_offer_list[i].price} and buy price {bid_offer_list[i].price}')

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
