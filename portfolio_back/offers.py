import requests

BASE_URLS = {'bittrex': 'https://api.bittrex.com/v3/', 'bitbay': 'https://bitbay.net/API/Public/'}
MARKETS_URLS = {'bittrex': 'https://api.bittrex.com/v3/markets/',
                'bitbay': 'https://api.bitbay.net/rest/trading/ticker'}
ORDERBOOK_URL_INFIXES = {'bittrex': 'markets/', 'bitbay': ''}
ORDERBOOK_URL_SUFFIXES = {'bittrex': '/orderbook', 'bitbay': '/orderbook.json'}
MARKETS_DICT_KEYS = {'bittrex': 'symbol', 'bitbay': 'items'}

SEPARATORS = {'bittrex': '-', 'bitbay': ''}


class Offer:
    def __init__(self, pair, transaction_type, quantity, price):
        self.pair = pair
        self.transaction_type = transaction_type[:3]
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f'{self.transaction_type} offer for {self.pair}, quantity = {self.quantity}, price = {self.price}'


def get_orders_from_api(site, market):
    try:
        headers = {'content-type': 'application/json'}
        currencies = market.split('-')
        response = requests.get(BASE_URLS[site] + ORDERBOOK_URL_INFIXES[site] + currencies[0] + SEPARATORS[site]
                                + currencies[1] + ORDERBOOK_URL_SUFFIXES[site], headers=headers)

        if 200 <= response.status_code < 300:
            return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def convert_json_to_offerlist(pair, from_api, how_many):
    offers = []
    for transaction_type in from_api.keys():
        for offer_json in from_api[transaction_type]:
            if isinstance(offer_json, dict):
                offers.append(Offer(pair=pair, transaction_type=transaction_type,
                                    quantity=float(offer_json['quantity']), price=float(offer_json['rate'])))
            else:
                offers.append(Offer(pair=pair, transaction_type=transaction_type,
                                    quantity=float(offer_json[1]), price=float(offer_json[0])))

    bid_offer_list = list(filter(lambda offer: offer.transaction_type == 'bid', offers))
    ask_offer_list = list(filter(lambda offer: offer.transaction_type == 'ask', offers))
    num_offers = min(how_many, len(bid_offer_list), len(ask_offer_list))
    bid_offer_list = bid_offer_list[:num_offers]
    ask_offer_list = ask_offer_list[:num_offers]

    return bid_offer_list + ask_offer_list


def get_offerlist(site, pairs, num_offers):
    res_offerlist = []
    for pair in pairs:
        from_api = get_orders_from_api(site, pair)
        current_market_offer_list = convert_json_to_offerlist(pair, from_api, num_offers)
        for offer in current_market_offer_list:
            res_offerlist.append(offer)

    return res_offerlist


def get_bidlist(pair, num_offers):
    temp_offerdict = {}
    for site in BASE_URLS.keys():
        temp_offerdict[site] = list(filter(lambda offer: offer.transaction_type == 'bid',
                                           get_offerlist(site, [pair], num_offers)))

    return temp_offerdict


def get_data(site_list, pairs):
    offers = {}
    for site in site_list:
        offers[site] = get_offerlist(site, pairs, 25)

    return offers


def get_site_markets_json(site):
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get(MARKETS_URLS[site], headers=headers)

        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None


def convert_site_pairs_to_list(markets_json, site):
    if isinstance(markets_json, dict):
        return [*markets_json[MARKETS_DICT_KEYS[site]].keys()]
    else:
        return [market[MARKETS_DICT_KEYS[site]] for market in markets_json]


def get_markets_list(site):
    markets_json = get_site_markets_json(site)
    return convert_site_pairs_to_list(markets_json, site)


def find_common_pairs(pairs1, pairs2):
    return [market for market in pairs1 if market in pairs2]


def get_common_pairs_for_sites(site1, site2):
    site1_markets = get_markets_list(site1)
    site2_markets = get_markets_list(site2)
    return find_common_pairs(site1_markets, site2_markets)


def print_list(ls):
    for item in ls:
        print(item)
