import math

from Bitbay import Bitbay
from Bittrex import Bittrex

API = {
    'bitbay': Bitbay(),
    'bittrex': Bittrex()
}


def find_common_pairs(first, second):
    return list(set(first).intersection(second))


def get_price_buy(volume, rate, taker_fee):
    return volume * (1 + (volume * taker_fee)) * rate


def get_price_sell(volume, rate, taker_fee):
    return volume * (1 - volume * taker_fee) * rate


def find_best_arbitrage(bid_offers, ask_offers, ask_taker, bid_taker, ask_transfer):
    best_arbitrage = {
        'buy': 0,
        'sell': 0,
        'invest': math.inf,
        'earn': -math.inf
    }
    for offer in ask_offers:
        rate = offer['rate']
        quantity = offer['quantity']

        hold_volume = quantity - ask_transfer
        investment = get_price_buy(quantity, rate, ask_taker)
        revenue = 0
        num_of_offer = 0
        while hold_volume > 0 and num_of_offer < len(bid_offers):
            volume_to_buy = bid_offers[num_of_offer]['quantity']
            if hold_volume >= volume_to_buy:
                revenue += get_price_sell(volume_to_buy, bid_offers[num_of_offer]['rate'], bid_taker)
                hold_volume -= volume_to_buy
            num_of_offer += 1

        if revenue - investment > best_arbitrage['earn'] - best_arbitrage['invest']:
            best_arbitrage = {
                'buy': quantity,
                'sell': quantity - hold_volume - ask_transfer,
                'invest': investment,
                'earn': revenue
            }

    return best_arbitrage


if __name__ == '__main__':
    # Ex. 1
    common = find_common_pairs(API['bitbay'].markets, API['bittrex'].markets)
    print(common)

    # Ex. 2
    bitbay_asks, bitbay_bids = API['bitbay'].orderbook('BTC', 'EUR')
    bittrex_asks, bittrex_bids = API['bittrex'].orderbook('BTC', 'EUR')
    arbitrage = find_best_arbitrage(bitbay_bids, bittrex_asks, API['bittrex'].taker_fee, API['bitbay'].taker_fee,
                                    API['bittrex'].transfer_fee('BTC'))
    print(arbitrage)
