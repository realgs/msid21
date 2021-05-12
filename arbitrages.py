import random

from offers import print_list, count_profit, get_data, update_transaction_fees, get_common_markets_for_sites


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
               '{:.5f} {}. Ratio is: {:.5f}% (with respect to ask value - {:.5f} {}), quantity is {:.5f},' \
               ' price is {:.5f}'. format(self.profit, self.market.split('-')[1], self.percentage * 100,
                                          self.quantity * self.ask.price, self.market.split('-')[1], self.quantity,
                                          self.ask.price)


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
    print_list(sorted(arbitrages, key=lambda arbitrage: arbitrage.percentage, reverse=True))


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
