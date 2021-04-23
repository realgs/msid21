import random

import requests

BASE_CURRENCY = 'USD'
CRYPTOS = ['BTC', 'LTC', 'ETH']
FEES = {'bittrex': {'taker': 0.25, 'transfer': {'BTC': 0.0005, 'LTC': 0.01, 'ETH': 0.006}},
        'bitbay': {'taker': 0.4, 'transfer': {'BTC': 0.0001, 'LTC': 0.1, 'ETH': 0.01}}}

BASE_URLS = {'bittrex': 'https://api.bittrex.com/v3/', 'bitbay': 'https://bitbay.net/API/Public/'}
GET_MARKETS_URLS = {'bittrex': 'https://api.bittrex.com/v3/markets/',
                    'bitbay': 'https://api.bitbay.net/rest/trading/ticker'}
FEES_URL_INFIXES = {'bittrex': 'currencies'}
ORDERBOOK_URL_INFIXES = {'bittrex': 'markets/', 'bitbay': ''}
ORDERBOOK_URL_SUFFIXES = {'bittrex': '/orderbook', 'bitbay': '/orderbook.json'}
MARKETS_DICT_KEYS = {'bittrex': 'symbol', 'bitbay': 'items'}

SEPARATORS = {'bittrex': '-', 'bitbay': ''}


class Offer:
    def __init__(self, market, transaction_type, quantity, price):
        self.market = market
        self.transaction_type = transaction_type[:3]
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.market}, quantity = {self.quantity}, price = {self.price}'


class Arbitrage:
    def __init__(self, bid_site, ask_site, market, quantity, profit, percentage, bid, ask):
        self.bid_site = bid_site
        self.ask_site = ask_site
        self.market = market
        self.quantity = quantity
        self.profit = profit
        self.percentage = percentage
        self.bid = bid
        self.ask = ask

    def __repr__(self):
        return f'Profit for arbitrage {self.bid_site} - {self.ask_site} {self.market} is ' + \
               '{:.5f}$. Ratio is: {:.5f}% (with respect to ask value - {:.5f}$), quantity is {:.5f}, price is {:.5f}'.\
                   format(self.profit, self.percentage * 100, self.quantity * self.ask.price, self.quantity,
                          self.ask.price)


def get_transaction_fees_json(site):
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get(BASE_URLS[site] + FEES_URL_INFIXES[site], headers=headers)

        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def get_transaction_fees_dict(from_api):
    res_dict = {}
    for currency in from_api:
        res_dict[currency['symbol']] = float(currency['txFee'])

    return res_dict


def update_transaction_fees(site):
    from_api = get_transaction_fees_json(site)
    FEES[site]['transfer'] = get_transaction_fees_dict(from_api)


def get_orders_from_api(site, market):
    try:
        headers = {'content-type': 'application/json'}
        currencies = market.split('-')
        response = requests.get(BASE_URLS[site] + ORDERBOOK_URL_INFIXES[site] + currencies[0] + SEPARATORS[site]
                                + currencies[1] + ORDERBOOK_URL_SUFFIXES[site], headers=headers)

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

    bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', offers))
    ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', offers))
    num_offers = min(how_many, len(bid_offer_list), len(ask_offer_list))
    bid_offer_list = bid_offer_list[:num_offers]
    ask_offer_list = ask_offer_list[:num_offers]

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
        offers[site] = get_offerlist(site, markets, 25)

    return offers


def get_site_markets_json(site):
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get(GET_MARKETS_URLS[site], headers=headers)

        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def convert_site_markets_to_list(markets_json, site):
    if isinstance(markets_json, dict):
        return [*markets_json[MARKETS_DICT_KEYS[site]].keys()]
    else:
        return [market[MARKETS_DICT_KEYS[site]] for market in markets_json]


def get_markets_list(site):
    markets_json = get_site_markets_json(site)
    return convert_site_markets_to_list(markets_json, site)


def find_common_markets(markets1, markets2):
    return [market for market in markets1 if market in markets2]


def get_common_markets_for_sites(site1, site2):
    site1_markets = get_markets_list(site1)
    site2_markets = get_markets_list(site2)
    return find_common_markets(site1_markets, site2_markets)


def print_list(ls):
    for item in ls:
        print(item)


def count_ratio(offer1, offer2):
    return 1 - (offer2.price - offer1.price) / offer2.price


def count_profit(bid, bid_site, ask, ask_site):
    quantity_in_deposit = ask.quantity - FEES[bid_site]['transfer'][bid.market.split('-')[0]] \
        if bid.market.split('-')[0] in FEES[bid_site]['transfer'].keys() else ask.quantity
    quantity_in_deposit = quantity_in_deposit - FEES[ask_site]['transfer'][ask.market.split('-')[0]] \
        if ask.market.split('-')[0] in FEES[ask_site]['transfer'].keys() else quantity_in_deposit
    quantity = max(quantity_in_deposit, bid.quantity)
    quantity = max(quantity, 0)
    bid_value = quantity * bid.price * (1 - FEES[bid_site]['taker'])
    ask_value = quantity * ask.price * (1 - FEES[ask_site]['taker'])

    profit = bid_value - ask_value
    profit_percentage = profit / (ask.price * quantity)  # if ask.price * quantity != 0 else 0

    return profit, profit_percentage, quantity


def find_best_arbitrage(bids, asks, site_list):
    site_pairs = [(site_list[0], site_list[1]), (site_list[1], site_list[0])]
    biggest_profit = None
    best_bid = None
    best_ask = None
    best_site_pair = ()
    best_arbitrage_results = ()
    for pair in site_pairs:
        for bid in bids[pair[0]]:
            for ask in asks[pair[1]]:
                biggest_profit = count_profit(bid, pair[0], ask, pair[1])[0] if not biggest_profit else biggest_profit
                if count_profit(bid, pair[0], ask, pair[1])[0] >= biggest_profit:
                    biggest_profit = count_profit(bid, pair[0], ask, pair[1])[0]
                    best_bid = bid
                    best_ask = ask
                    best_arbitrage_results = count_profit(bid, pair[0], ask, pair[1])
                    best_site_pair = pair

    return best_bid, best_ask, best_site_pair, best_arbitrage_results


def get_profit_info(bid, bid_site, ask, ask_site, best_arbitrage_results):
    return Arbitrage(bid_site, ask_site, bid.market, best_arbitrage_results[2], best_arbitrage_results[0],
                     best_arbitrage_results[1], bid, ask)


def get_arbitrages(site_list, markets, offers):
    bid_offers = {}
    ask_offers = {}
    arbitrage_list = []
    for market_name in markets:
        for site in site_list:
            temp_offer_list = list(filter(lambda offer: offer.market == market_name, offers[site]))
            bid_offers[site] = list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))
            ask_offers[site] = list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))

        best_bid, best_ask, best_sites_pair, best_arbitrage_results = \
            find_best_arbitrage(bid_offers, ask_offers, site_list)

        arbitrage_list.append(get_profit_info(best_bid, best_sites_pair[0], best_ask, best_sites_pair[1],
                                              best_arbitrage_results))
        bid_offers.clear()
        ask_offers.clear()

    return arbitrage_list


def print_arbitrages(arbitrages):
    print_list(sorted(arbitrages, key=lambda arbitrage: arbitrage.profit, reverse=True))


def get_random_arbitrages(site_list, market_list):
    markets = random.sample(market_list, 3)
    data = get_data(site_list, markets)
    arbitrages = get_arbitrages(site_list, markets, data)
    print_arbitrages(arbitrages)
    print()


def get_all_arbitrages(site_list, market_list):
    data = get_data(site_list, market_list)
    arbitrages = get_arbitrages(site_list, market_list, data)
    print_arbitrages(arbitrages)


if __name__ == '__main__':
    update_transaction_fees('bittrex')
    sites = ['bittrex', 'bitbay']
    available_markets = get_common_markets_for_sites(sites[0], sites[1])
    get_random_arbitrages(sites, available_markets)
    get_all_arbitrages(sites, available_markets)
