import constants
import alphavantage
import constants_alphavantage


def single_transaction(ask, bid, askFee, bidFee):
    volume = min(ask[1], bid[1])
    quantity_purchased = volume * (1 - askFee)
    cost = volume * ask[0]
    takings = quantity_purchased * bid[0] * (1 - bidFee)
    earnings = takings - cost
    is_worth = True if earnings > 0 else False
    return {constants.ST_VOLUME: volume, constants.ST_PURCHASED: quantity_purchased, constants.ST_EARNINGS: earnings,
            constants.ST_ISWORTH: is_worth}


def subtract_from_offers(offers, quantity):
    if quantity == offers[0][1]:
        del offers[0]
    else:
        offers[0][1] -= quantity
    return offers


def calc_arbitrage(market1, market2, pair):
    try:
        asks = market1.get_orderbook(market1.pairs[pair], constants.CA_ANALYZED_OFFERS)[constants.ASKS]
        bids = market2.get_orderbook(market2.pairs[pair], constants.CA_ANALYZED_OFFERS)[constants.BIDS]
    except:
        return {constants.CA_BUY: market1, constants.CA_SELL: market2, constants.CA_PAIR: pair,
                constants.CA_EARNINGS: None}

    if asks == [] or bids == []:
        return {constants.CA_BUY: market1, constants.CA_SELL: market2, constants.CA_PAIR: pair, constants.CA_EARNINGS: None}

    no_offers = False
    earnings = 0
    transaction = single_transaction(asks[0], bids[0], market1.taker_fee, market2.taker_fee)
    if not transaction[constants.ST_ISWORTH]:
        earnings += transaction[constants.ST_EARNINGS]

    while transaction[constants.ST_ISWORTH] and not no_offers:
        earnings += transaction[constants.ST_EARNINGS]
        subtract_from_offers(asks, transaction[constants.ST_VOLUME])
        subtract_from_offers(bids, transaction[constants.ST_PURCHASED])
        if len(bids) > 0 and len(asks) > 0:
            transaction = single_transaction(asks[0], bids[0], market1.taker_fee, market2.taker_fee)
        else:
            no_offers = True

    return {constants.CA_BUY: market1, constants.CA_SELL: market2, constants.CA_PAIR: pair, constants.CA_EARNINGS: earnings}


def valuation(market, cryptocurrency, quantity):
    result = {constants.STATUS: constants.OK}
    try:
        pair = market.pairs[(cryptocurrency, 'USDT')]
        bids = market.get_orderbook(pair, 50)[constants.BIDS]
    except:
        return result[constants.STATUS: constants.FAIL]

    if bids == []:
        return result[constants.STATUS: constants.FAIL]

    value = 0

    while quantity > 0 and len(bids) > 0:
        bid_rate = bids[0][0]
        bid_quantity = bids[0][1]
        volume = min(bid_quantity, quantity)
        quantity -= volume
        earnings = volume * bid_rate * (1 - market.taker_fee)
        value += earnings
        subtract_from_offers(bids, volume)

    result[constants.V_VALUE] = value
    result[constants.V_LEFT] = quantity

    return result


def value_in_base(base, in_usd):
    result = {constants.STATUS: constants.OK}
    if base == 'USD':
        result[constants.VALUE] = in_usd
    else:
        rate = alphavantage.get_offer('USD', base)
        if rate[constants.STATUS] == constants_alphavantage.OK:
            price = rate[constants.BID]
            value = in_usd * price
            result[constants.VALUE] = value
        else:
            result[constants.STATUS] = constants.FAIL
    return result
