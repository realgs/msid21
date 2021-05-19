import Bitbay
import Binance
import constants


def get_common_pairs(market1, market2):
    return list(market1.pairs.intersection(market2.pairs))


def subtract_from_offers(offers, quantity):
    result = offers
    if quantity == offers[0][1]:
        del result[0]
    else:
        result[0][1] -= quantity
    return result


def the_same_order(market1, market2, pair):
    return market1.get_order()[pair] == market2.get_order()[pair]


def value_in_USD(market, currency, quantity):
    pair = None
    if frozenset([currency, "USDT"]) in market.get_pairs():
        pair = frozenset([currency, "USDT"])
    elif frozenset([currency, "USD"]) in market.get_pairs():
        pair = frozenset([currency, "USD"])
    else:
        return None
    price = market.get_orderbook(market.get_pairs()[pair])[constants.ASKS][0][0]
    return price * quantity

def transaction(ask, bid, askFee, bidFee):
    volume = min(ask[1], bid[1])
    quantityPurchased = volume * (1 - askFee)
    cost = volume * ask[0]
    takings = quantityPurchased * bid[0] * (1 - bidFee)
    earnings = takings - cost
    if earnings > 0:
        isWorth = True
    else:
        isWorth = False
    return [volume, quantityPurchased, earnings, isWorth]

def calc_arbitrage(market1, market2, pair):
    base = market1.get_order()[pair]["first"]
    quote = market1.get_order()[pair]["second"]

    if not the_same_order(market1, market2, pair):
        asks = market1.get_orderbook(market1.get_pairs()[pair])[constants.ASKS]
        b = market2.get_orderbook(market2.get_pairs()[pair])[constants.ASKS]
        bids = []
        for bid in b:
            bids.append([1/bid[0], bid[0]*bid[1]])
    else:
        asks = market1.get_orderbook(market1.get_pairs()[pair])[constants.ASKS]
        bids = market2.get_orderbook(market2.get_pairs()[pair])[constants.BIDS]

    if asks == [] or bids == []:
        return {"buy": market1, "sell": market2, "pair": pair, "earnings": None, "earningsUSD": None}

    askFee = market1.get_taker_fee()
    bidFee = market2.get_taker_fee()
    earnings = 0

    trans = transaction(asks[0], bids[0], askFee, bidFee)

    if not trans[3]:
        earnings += trans[2]

    while len(bids) > 0 and len(asks) > 0 and trans[3]:
        earnings += trans[2]
        subtract_from_offers(asks, trans[0])
        subtract_from_offers(bids, trans[1])
        if len(bids) > 0 and len(asks) > 0:
            trans = transaction(asks[0], bids[0], askFee, bidFee)

    earnings -= market1.get_withdrawal_fees()[quote]

    earningsUSD = value_in_USD(market2, quote, earnings)

    return {"buy": market1, "sell": market2, "pair": pair, "earnings": earnings, "earningsUSD": earningsUSD}

def calc_arbitrage_for_all():
    bitbay = Bitbay.create_market()
    binance = Binance.create_market()
    common_pairs = get_common_pairs(bitbay, binance)

    result = []

    for pair in common_pairs:
        arbitrage = calc_arbitrage(bitbay, binance, pair)
        if not arbitrage['earningsUSD'] == None:
            result.append(arbitrage)

    for pair in common_pairs:
        arbitrage = calc_arbitrage(binance, bitbay, pair)
        if not arbitrage['earningsUSD'] == None:
            result.append(arbitrage)

    return result


def print_sorted_by_arbitrage():
    res = calc_arbitrage_for_all()
    res.sort(key=lambda x: x["earningsUSD"], reverse=True)
    for i in res:
        print("buy:", i["buy"].name, "sell:", i["sell"].name, "pair:", i["sell"].get_pairs()[i["pair"]], "profit:", str(i["earnings"]), "USD:", str(i["earningsUSD"]))


if __name__ == '__main__':
    print_sorted_by_arbitrage()
