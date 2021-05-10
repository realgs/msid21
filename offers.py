import requests

BASE_CURRENCY = 'USD'
CRYPTOS = ['BTC', 'LTC', 'ETH']
FEES = {'bittrex': {'taker': 0.25, 'transfer': {'BTC': 0.0005, 'LTC': 0.01, 'ETH': 0.006}},
        'bitbay': {'taker': 0.4, 'transfer': {'AAVE': 0.23, 'ALG': 258, 'AMLT': 965, 'BAT': 29, 'BCC': 0.001,
                                              'BCP': 665, 'BOB': 4901, 'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001,
                                              'COMP': 0.025, 'DAI': 19, 'DASH': 0.001, 'DOT': 0.10, 'EOS': 0.10,
                                              'ETH': 0.006, 'EXY': 52, 'GAME': 279, 'GGC': 6, 'GNT': 66, 'GRT': 11,
                                              'LINK': 1.85, 'LML': 150, 'LSK': 0.30, 'LTC': 0.001, 'LUNA': 0.02,
                                              'MANA': 27, 'MKR': 0.014, 'NEU': 109, 'NPXS': 2240, 'OMG': 3.50,
                                              'PAY': 278, 'QARK': 1133, 'REP': 1.55, 'SRN': 2905, 'SUSHI': 2.50,
                                              'TRX': 1, 'UNI': 0.70, 'USDC': 75.50, 'USDT': 37, 'XBX': 3285, 'XIN': 5,
                                              'XLM': 0.005, 'XRP': 0.10, 'XTZ': 0.10, 'ZEC': 0.004, 'ZRX': 16.00}}}

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
