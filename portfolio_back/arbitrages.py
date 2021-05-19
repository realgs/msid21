import requests

from .offers import print_list, get_common_pairs_for_sites, BASE_URLS, get_data

FEES_URL_INFIXES = {'bittrex': 'currencies'}
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
        return f'{self.bid_site[:4]} - {self.ask_site[:4]} {self.market} ' + \
               '{:.5f}{}'.format(self.profit, self.market.split('-')[1])


def get_transaction_fees_json(site):
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get(BASE_URLS[site] + FEES_URL_INFIXES[site], headers=headers)

        if 200 <= response.status_code < 300:
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


def count_profit(bid, bid_site, ask, ask_site):
    quantity_in_deposit = ask.quantity - FEES[bid_site]['transfer'][bid.pair.split('-')[0]] \
        if bid.pair.split('-')[0] in FEES[bid_site]['transfer'].keys() else ask.quantity
    quantity_in_deposit = quantity_in_deposit - FEES[ask_site]['transfer'][ask.pair.split('-')[0]] \
        if ask.pair.split('-')[0] in FEES[ask_site]['transfer'].keys() else quantity_in_deposit
    quantity = max(quantity_in_deposit, bid.quantity)
    quantity = max(quantity, 0)
    bid_value = quantity * bid.price * (1 - FEES[bid_site]['taker'])
    ask_value = quantity * ask.price * (1 - FEES[ask_site]['taker'])

    profit = bid_value - ask_value
    profit_percentage = profit / (ask.price * quantity)

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
    return Arbitrage(bid_site, ask_site, bid.pair, best_arbitrage_results[2], best_arbitrage_results[0],
                     best_arbitrage_results[1], bid, ask)


def get_arbitrages(site_list, pairs, offers):
    bid_offers = {}
    ask_offers = {}
    arbitrage_list = []
    for pair in pairs:
        for site in site_list:
            temp_offer_list = list(filter(lambda offer: offer.pair == pair, offers[site]))
            bid_offers[site] = list(filter(lambda offer: offer.transaction_type == 'bid', temp_offer_list))
            ask_offers[site] = list(filter(lambda offer: offer.transaction_type == 'ask', temp_offer_list))

        if bid_offers[site_list[0]] and bid_offers[site_list[1]] and ask_offers[site_list[0]] and \
                bid_offers[site_list[1]]:
            best_bid, best_ask, best_sites_pair, best_arbitrage_results = \
                find_best_arbitrage(bid_offers, ask_offers, site_list)

            arbitrage_list.append(get_profit_info(best_bid, best_sites_pair[0], best_ask, best_sites_pair[1],
                                                  best_arbitrage_results))
            bid_offers.clear()
            ask_offers.clear()

    return sorted(arbitrage_list, key=lambda arbitrage: arbitrage.percentage, reverse=True)


def print_arbitrages(arbitrages):
    print_list(sorted(arbitrages, key=lambda arbitrage: arbitrage.percentage, reverse=True))


def get_arbitrage(currency):
    update_transaction_fees('bittrex')
    sites = ['bittrex', 'bitbay']
    available_pairs = [pair for pair in get_common_pairs_for_sites(sites[0], sites[1]) if currency in pair]
    data = get_data(sites, available_pairs)
    return get_arbitrages(sites, available_pairs, data)[0]
