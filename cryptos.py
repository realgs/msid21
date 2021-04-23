import time

import requests

BASE_CURRENCY = 'USD'
CRYPTOS = ['BTC', 'LTC', 'ETH']
FEES = {'bittrex': {'taker': 0.25, 'transfer': {'BTC': 0.0005, 'LTC': 0.01, 'ETH': 0.006}},
        'bitbay': {'taker': 0.4, 'transfer': {'BTC': 0.0001, 'LTC': 0.1, 'ETH': 0.01}}}

BASE_URLS = {'bittrex': 'https://api.bittrex.com/v3/markets/', 'bitbay': 'https://bitbay.net/API/Public/'}
SEPARATORS = {'bittrex': '-', 'bitbay': ''}
TYPE_URL_SUFFIXES = {'bittrex': '', 'bitbay': '.json'}


class Offer:
    def __init__(self, market, transaction_type, quantity, price):
        self.market = market
        self.transaction_type = transaction_type[:3]
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.price}'


def get_orders_from_api(site, market):
    try:
        headers = {'content-type': 'application/json'}
        currencies = market.split('-')
        response = requests.get(BASE_URLS[site] + currencies[0] + SEPARATORS[site] + currencies[1] + '/orderbook' +
                                TYPE_URL_SUFFIXES[site], headers=headers)

        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def convert_json_to_offerlist(market, from_api, how_many):
    offers = []
    for transaction_type in from_api.keys():
        for offer_json in from_api[transaction_type]:
            if isinstance(offer_json, dict):
                offers.append(Offer(market=market, transaction_type=transaction_type,
                                    quantity=float(offer_json['quantity']), price=float(offer_json['rate'])))
            else:
                offers.append(Offer(market=market, transaction_type=transaction_type,
                                    quantity=float(offer_json[1]), price=float(offer_json[0])))

    bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', offers))[:how_many]
    ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', offers))[:how_many]

    return bid_offer_list + ask_offer_list


def get_offerlist(site, markets, num_offers):
    res_offerlist = []
    for market in markets:
        from_api = get_orders_from_api(site, market)
        current_market_offer_list = convert_json_to_offerlist(market, from_api, num_offers)
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
