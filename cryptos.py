import time

import requests

BASE_CURRENCY = 'USD'
CRYPTOS = ['BTC', 'LTC', 'ETH']
FEES = {'bittrex': {'taker': 0.25, 'transfer': {'BTC': 0.0005, 'LTC': 0.01, 'ETH': 0.006}},
        'bitbay': {'taker': 0.4, 'transfer': {'BTC': 0.0001, 'LTC': 0.1, 'ETH': 0.01}}}


class Offer:
    def __init__(self, market, transaction_type, quantity, price):
        self.market = market
        self.transaction_type = transaction_type[:3]
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.price}'


def get_orders_from_api(site, market, how_many):
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
        from_api = get_orders_from_api(site, market, num_offers)
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


def count_profit(bid, bid_site, ask, ask_site):
    quantity_in_deposit = ask.quantity * (1 - FEES[bid_site]['transfer'][bid.market.split('-')[0]]) * \
                          (1 - FEES[ask_site]['transfer'][ask.market.split('-')[0]])
    quantity = quantity_in_deposit if quantity_in_deposit < bid.quantity else bid.quantity
    bid_value = quantity * bid.price * (1 - FEES[bid_site]['taker'])
    ask_value = quantity * ask.price * (1 - FEES[ask_site]['taker'])

    profit = bid_value - ask_value
    profit_percentage = profit / (ask.price * quantity)

    return profit, profit_percentage


def print_ratio_info(offer1, offer2, ratio_type):
    print(f'{offer1.market} {ratio_type} ratio: ' + '{:.1f}%'.format(count_ratio(offer1, offer2) * 100) +
          f' for prices: {offer2.price}$ and {offer1.price}$')


def print_profit_info(bid, bid_site, ask, ask_site):
    profits = count_profit(bid, bid_site, ask, ask_site)
    quantity = bid.quantity if bid.quantity < ask.quantity else ask.quantity
    print(f'Profit for arbitrage {bid_site} - {ask_site} {bid.market} is ' +
          '{:.2f}$. Ratio is: {:.1f}% (with respect to ask value - {:.2f}$), quantity is {:.5f}, price is {:.2f}'
          .format(profits[0], profits[1] * 100, quantity * ask.price, quantity, ask.price))


def print_ratios(bid_offers, ask_offers, sites):
    print_ratio_info(ask_offers[sites[0]], ask_offers[sites[1]], 'ask')
    print_ratio_info(bid_offers[sites[0]], bid_offers[sites[1]], 'bid')
    print_ratio_info(bid_offers[sites[0]], ask_offers[sites[1]], 'arbitrage')
    print_profit_info(bid_offers[sites[0]], sites[0], ask_offers[sites[1]], sites[1])
    print_ratio_info(bid_offers[sites[1]], ask_offers[sites[0]], 'reverse arbitrage')
    print_profit_info(bid_offers[sites[1]], sites[1], ask_offers[sites[0]], sites[0])


def print_data(sites, markets, offers):
    print(f'{sites[0]} - {sites[1]} ratios:')
    bid_offers = {}
    ask_offers = {}
    for market_name in markets:
        for site in sites:
            temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers[site]))
            bid_offers[site] = list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))[0]
            ask_offers[site] = list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))[0]

        print_ratios(bid_offers, ask_offers, sites)
        bid_offers.clear()
        ask_offers.clear()


def get_datastream():
    market_list = [market + '-' + BASE_CURRENCY for market in CRYPTOS]
    site_list = ['bittrex', 'bitbay']
    while True:
        data = get_data(site_list, market_list)
        print_data(site_list, market_list, data)
        print('\n')
        time.sleep(5)


if __name__ == '__main__':
    get_datastream()
