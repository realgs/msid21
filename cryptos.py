import time

import requests


class Offer:
    def __init__(self, market, transaction_type, quantity, price):
        self.market = market
        self.transaction_type = transaction_type[:3]
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.price}'


def get_offers_from_api(site, market, how_many):
    try:
        if site == 'bittrex':
            return get_orders_from_bittrex(market, how_many)
        elif site == 'bitbay':
            return get_orders_from_bitbay(market)
        else:
            print("ERROR. API not recognized; empty list returned")
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def get_orders_from_bittrex(market, how_many):
    return requests.get(f'https://api.bittrex.com/v3/markets/{market}/orderbook?depth={how_many}').json()


def get_orders_from_bitbay(market):
    currencies = market.split('-')
    return requests.get(f'https://bitbay.net/API/Public/{currencies[0]}/{currencies[1]}/orderbook.json').json()


def convert_json_to_offerlist(site, market, from_api, how_many):
    if site == 'bittrex':
        return convert_bittrex_json_to_offerlist(market, from_api)
    elif site == 'bitbay':
        return convert_bitbay_json_to_offerlist(market, from_api, how_many)
    else:
        print("ERROR. API not recognized; empty list returned")


def convert_bittrex_json_to_offerlist(market, data):
    offers = []
    for transaction_type in ['bid', 'ask']:
        for offer_json in data[transaction_type]:
            offers.append(Offer(market=market, transaction_type=transaction_type,
                                quantity=float(offer_json['quantity']), price=float(offer_json['rate'])))

    return offers


def convert_bitbay_json_to_offerlist(market, data, how_many):
    offers = []
    for transaction_type in ['bids', 'asks']:
        for offer_json in data[transaction_type]:
            offers.append(Offer(market=market, transaction_type=transaction_type,
                                quantity=float(offer_json[1]), price=float(offer_json[0])))

    bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', offers))[:how_many]
    ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', offers))[:how_many]
    return bid_offer_list + ask_offer_list


def get_offerlist(site, markets, num_offers):
    res_offerlist = []
    for market in markets:
        from_api = get_offers_from_api(site, market, num_offers)
        current_market_offer_list = convert_json_to_offerlist(site, market, from_api, num_offers)
        for offer in current_market_offer_list:
            res_offerlist.append(offer)

    return res_offerlist


def get_data(site_list, markets):
    offers = {}
    for site in site_list:
        offers[site] = get_offerlist(site, markets, 1)

    return offers


def print_list(ls):
    for item in ls:
        print(item)


def count_ratio(offer1, offer2):
    return 1 - (offer2.price - offer1.price) / offer2.price


def print_ratio_info(offer1, offer2, ratio_type):
    print(f'{offer1.market} {ratio_type} ratio: ' + '{:.1f}%'.format(count_ratio(offer1, offer2) * 100) +
          f' for prices: {offer2.price}$ and {offer1.price}$')


def print_ratios(sites, markets, offers):
    print(f'{sites[0]} - {sites[1]} ratios:')
    bid_offers = []
    ask_offers = []
    for market_name in markets:
        for site in sites:
            temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers[site]))
            bid_offers.append(list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))[0])
            ask_offers.append(list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))[0])

        print_ratio_info(ask_offers[0], ask_offers[1], 'ask')
        print_ratio_info(bid_offers[0], bid_offers[1], 'bid')
        print_ratio_info(bid_offers[0], ask_offers[1], 'arbitrage')
        print_ratio_info(bid_offers[1], ask_offers[0], 'reverse arbitrage')
        bid_offers.clear()
        ask_offers.clear()


def get_datastream(markets):
    base_currency = 'USD'
    market_list = [market + '-' + base_currency for market in markets]
    site_list = ['bittrex', 'bitbay']
    while True:
        data = get_data(site_list, market_list)
        print_ratios(site_list, market_list, data)
        print('\n')
        time.sleep(5)
