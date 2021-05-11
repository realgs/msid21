import requests
import time

DELAY = 5
APIS = {"bitbay": {"orderbook": "https://bitbay.net/API/Public/{}/orderbook.json",
                   "markets": "https://api.bitbay.net/rest/trading/ticker",
                   "fees":
                       {"taker_fee": 0.0042,
                       "BTC_fee": 0.0005}},
        "bittrex": {"orderbook": "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both",
                    "markets": "https://api.bittrex.com/v3/markets",
                    "fees":
                        {"taker_fee": 0.0075,
                         "BTC_fee": 0.0005}}}


def get_common_currencies(market1, market2):
    common = []
    for i in market1:
        if i in market2:
            common.append(i)
    return common


def get_markets(api_name):
    markets = []
    try:
        req = requests.get(APIS[api_name]['markets'])
        if 199 < req.status_code < 300:
            req = req.json()
            if api_name == "bittrex":
                for i in range(0, len(req)):
                    markets.append(req[i]['symbol'])
                return markets
            if api_name == "bitbay":
                for i in req['items'].keys():
                    markets.append(i)
                return markets
            else:
                return None
    except requests.exceptions:
        return None


def get_offers(api_name, curr1, curr2):
    try:
        if api_name == "bitbay":
            offers = requests.get(APIS[api_name]['orderbook'].format(curr1 + curr2))
            if 199 < offers.status_code < 300:
                return offers.json()
        if api_name == "bittrex":
            offers = requests.get(APIS[api_name]["orderbook"].format(curr2, curr1))
            if 199 < offers.status_code < 300:
                return offers.json()
        else:
            return None
    except requests.exceptions:
        return None


def possible_arbitrage(selling_price, buying_price):
    return selling_price > buying_price


def bid_with_fees(bid, fees):
    return bid * (1 - fees['taker_fee']) - fees['BTC_fee']


def ask_with_fees(ask, fees):
    return ask * (1 + fees['taker_fee']) + fees['BTC_fee']


def arbitrage(bitbay_offer, bittrex_offer):
    bids_bitbay = bitbay_offer['bids']
    asks_bitbay = bitbay_offer['asks']

    bids_bittrex = bittrex_offer['result']['buy']
    asks_bittrex = bittrex_offer['result']['sell']

    i = 0
    j = 0
    amount_of_res_to_arb = 0
    profit = 0
    while possible_arbitrage(bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees']), ask_with_fees(asks_bitbay[j][0], APIS['bitbay']['fees'])):
        amount_of_res_to_arb += min(asks_bitbay[i][1], bids_bittrex[i]['Quantity'])
        profit += bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees']) - ask_with_fees(asks_bitbay[j][0], APIS['bitbay']['fees'])
        if asks_bitbay[i][1] == bids_bittrex[i]['Quantity']:
            i += 1
            j += 1
        if asks_bitbay[i][1] < bids_bittrex[i]['Quantity']:
            j += 1
            bids_bittrex[i]['Quantity'] = bids_bittrex[i]['Quantity'] - asks_bitbay[i][1]
        if asks_bitbay[i][1] > bids_bittrex[i]['Quantity']:
            i += 1
            asks_bitbay[i][1] = asks_bitbay[i][1] - bids_bittrex[i]['Quantity']

    while possible_arbitrage(bid_with_fees(bids_bitbay[i][0], APIS['bitbay']['fees']), ask_with_fees(asks_bittrex[j]['Rate'], APIS['bittrex']['fees'])):
        amount_of_res_to_arb += min(asks_bittrex[i]['Quantity'], bids_bitbay[i][1])
        profit += bid_with_fees(bids_bitbay[i][0], APIS['bitbay']['fees']) - ask_with_fees(asks_bittrex[j]['Rate'], APIS['bittrex']['fees'])
        if asks_bittrex[i]['Quantity'] == bids_bitbay[i][1]:
            i += 1
            j += 1
        if asks_bittrex[i]['Quantity'] < bids_bitbay[i][1]:
            j += 1
            bids_bitbay[i][1] = bids_bitbay[i][1] - asks_bittrex[i]['Quantity']
        if asks_bittrex[i]['Quantity'] > bids_bitbay[i][1]:
            i += 1
            bids_bitbay[i][1] = bids_bitbay[i][1] - asks_bittrex[i]['Quantity']

    if profit == 0:
        profit = max(bid_with_fees(bids_bitbay[0][0], APIS['bitbay']['fees']) - ask_with_fees(asks_bittrex[0]['Rate'], APIS['bittrex']['fees']), bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees']) - ask_with_fees(asks_bitbay[i][0], APIS['bitbay']['fees']))
    return amount_of_res_to_arb, profit


def print_spread(bitbay_offer, bittrex_offer, base_curr):
    arb = arbitrage(bitbay_offer, bittrex_offer)
    if arb[0] == 0:
        print("arbitrage not possible")
    else:
        print("quantity of resources that can be subjected to arbitrage: " + str(arb[0]))
        print("profit in {} ".format(base_curr) + str(arb[1]))


if __name__ == '__main__':

    while True:
        bitbay = get_markets("bitbay")
        bittrex = get_markets("bittrex")
        common_curr = get_common_currencies(bitbay, bittrex)

        ranking = []

        for curr in common_curr:
            currencies = curr.split('-')
            offer1 = get_offers("bitbay", currencies[0], currencies[1])
            offer2 = get_offers("bittrex", currencies[0], currencies[1])
            print_spread(offer1, offer2, currencies[1])

            ranking.append((arbitrage(offer1, offer2)[1], curr))

        ranking = sorted(ranking, key=lambda tup: tup[0], reverse=True)
        print(ranking)

        time.sleep(DELAY)
