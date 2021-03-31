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


def get_offers_from_api(market, how_many):
    try:
        data = requests.get(f'https://api.bittrex.com/v3/markets/{market}/orderbook?depth={how_many}').json()
        return data
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")
        return None


def convert_json_to_offerlist(market, data):
    offers = []
    for transaction_type in ['bid', 'ask']:
        for offer_json in data[transaction_type]:
            offers.append(Offer(market=market, transaction_type=transaction_type,
                                quantity=float(offer_json['quantity']), price=float(offer_json['rate'])))

    return offers


def get_offerlist(markets, num_offers):
    res_offerlist = []
    for market in markets:
        from_api = get_offers_from_api(market, num_offers)
        current_market_offer_list = convert_json_to_offerlist(market, from_api)
        for offer in current_market_offer_list:
            res_offerlist.append(offer)

    return res_offerlist


def print_list(ls):
    for item in ls:
        print(item)


def count_ratio(bid, ask):
    if bid.market == ask.market:
        result = 1 - (ask.price - bid.price) / ask.price
    else:
        print("ERROR. Bid and ask are not from the same market")
        result = -1
    return result


def print_ratio_info(bid, ask, ratio):
    print(f'{bid.market} buy - sell ratio: ' + '{:.1f}%'.format(ratio * 100) +
          f' for sell price {ask.price} and buy price {bid.price}')


def print_ratios(markets, offers):
    for market_name in markets:
        temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers))
        bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))
        ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))
        bid = bid_offer_list[0]
        ask = ask_offer_list[0]
        ratio = count_ratio(bid, ask)
        print_ratio_info(bid, ask, ratio)


def get_datastream(markets):
    while True:
        offers = get_offerlist(markets, 1)
        print_ratios(markets, offers)
        print('\n')
        time.sleep(5)
