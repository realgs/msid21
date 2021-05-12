import requests
import time

DELAY = 5
APIS = {"bitbay": {"orderbook": "https://bitbay.net/API/Public/{}/orderbook.json",
                   "markets": "https://api.bitbay.net/rest/trading/ticker",
                   "fees":
                       {"taker_fee": 0.0042,
                        "transfer_fee": {"AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0, "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1, "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0, "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0, "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0}}},
        "bittrex": {"orderbook": "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both",
                    "markets": "https://api.bittrex.com/v3/markets",
                    "fees":
                        {"taker_fee": 0.0075,
                         "transfer_fee": {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5, 'EOS': 0.1, 'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25}}}}


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


def bid_with_fees(bid, fees, curr):
    return bid * (1 - fees['taker_fee']) - fees['transfer_fee'][curr]


def ask_with_fees(ask, fees, curr):
    return ask * (1 + fees['taker_fee']) + fees['transfer_fee'][curr]


def arbitrage(bitbay_offer, bittrex_offer, curr):
    bids_bitbay = bitbay_offer['bids']
    asks_bitbay = bitbay_offer['asks']

    bids_bittrex = bittrex_offer['result']['buy']
    asks_bittrex = bittrex_offer['result']['sell']

    i = 0
    j = 0
    amount_of_res_to_arb = 0
    profit = 0
    while possible_arbitrage(bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees'], curr), ask_with_fees(asks_bitbay[j][0], APIS['bitbay']['fees'], curr)):
        amount_of_res_to_arb += min(asks_bitbay[i][1], bids_bittrex[i]['Quantity'])
        profit += bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees'], curr) - ask_with_fees(asks_bitbay[j][0], APIS['bitbay']['fees'], curr)
        if asks_bitbay[i][1] == bids_bittrex[i]['Quantity']:
            i += 1
            j += 1
        if asks_bitbay[i][1] < bids_bittrex[i]['Quantity']:
            j += 1
            bids_bittrex[i]['Quantity'] = bids_bittrex[i]['Quantity'] - asks_bitbay[i][1]
        if asks_bitbay[i][1] > bids_bittrex[i]['Quantity']:
            i += 1
            asks_bitbay[i][1] = asks_bitbay[i][1] - bids_bittrex[i]['Quantity']

    while possible_arbitrage(bid_with_fees(bids_bitbay[i][0], APIS['bitbay']['fees'], curr), ask_with_fees(asks_bittrex[j]['Rate'], APIS['bittrex']['fees'], curr)):
        amount_of_res_to_arb += min(asks_bittrex[i]['Quantity'], bids_bitbay[i][1])
        profit += bid_with_fees(bids_bitbay[i][0], APIS['bitbay']['fees'], curr) - ask_with_fees(asks_bittrex[j]['Rate'], APIS['bittrex']['fees'], curr)
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
        profit = max(bid_with_fees(bids_bitbay[0][0], APIS['bitbay']['fees'], curr) - ask_with_fees(asks_bittrex[0]['Rate'], APIS['bittrex']['fees'], curr), bid_with_fees(bids_bittrex[i]['Rate'], APIS['bittrex']['fees'], curr) - ask_with_fees(asks_bitbay[i][0], APIS['bitbay']['fees'], curr))
    return amount_of_res_to_arb, profit


def print_spread(bitbay_offer, bittrex_offer, base_curr, curr):
    arb = arbitrage(bitbay_offer, bittrex_offer, curr)
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
            print_spread(offer1, offer2, currencies[1], currencies[0])

            ranking.append((arbitrage(offer1, offer2, currencies[0])[1], curr))

        ranking = sorted(ranking, key=lambda tup: tup[0], reverse=True)
        print(ranking)

        time.sleep(DELAY)
