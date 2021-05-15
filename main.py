import requests
import time

BITBAY_MARKETS = "https://api.bitbay.net/rest/trading/ticker"
BITBAY_ORDERBOOK = "https://bitbay.net/API/Public/"
BITBAY_ORDER = '/orderbook.json'
BITBAY_TAKER_FEE = 0.0043
BITTREX_MARKETS = "https://api.bittrex.com/v3/markets/"
BITTREX_ORDER = '/orderbook'
BITTREX_ORDERBOOK = "https://api.bittrex.com/v3/markets/"
BITTREX_TAKER_FEE = 0.0025
CONNECTION_FAILED = "Connection failed"
markets = ['bitbay', 'bittrex']
bitbay_transfer_fees = {"AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0,
                        "BOB": 11645.0, "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0,
                        "DASH": 0.001,
                        "DOT": 0.1, "EOS": 0.1, "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0,
                        "GRT": 84.0, "LINK": 2.7, "LML": 1500.0, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0,
                        "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0, "PAY": 1523.0, "QARK": 1019.0,
                        "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0, "USDT": 190.0,
                        "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0}
bittrex_transfer_fees = {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5,
                         'EOS': 0.1, 'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1,
                         'LTC': 0.01,
                         'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567,
                         'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25,
                         'ZRX': 25}
DEPTH = 5
DELAY = 5


def connect_with_api(url):
    try:
        response = requests.get(url)
        if response.status_code in range(200, 299):
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print(CONNECTION_FAILED)
        return None


def get_bitbay_data(bitbay_json):
    result = []

    bitbay_items = bitbay_json['items']
    bitbay_keys = bitbay_items.keys()

    for element in bitbay_keys:
        result.append(element)

    return result


def get_bittrex_data(bittrex_json):
    result = []

    for element in range(0, len(bittrex_json)):
        result.append(bittrex_json[element]['symbol'])

    return result


def get_common_markets(first_api, second_api):
    common_markets = []

    for elem in first_api:
        if elem in second_api:
            common_markets.append(elem)

    common_markets.sort()

    return common_markets


def search_offers_bittrex(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    bittrex_response = connect_with_api(BITTREX_ORDERBOOK + currency + BITTREX_ORDER)

    if bittrex_response:
        for i in range(depth):
            offers['bid_price'].append(float(bittrex_response['bid'][i]['rate']))
        for i in range(depth):
            offers['bid_amount'].append(float(bittrex_response['bid'][i]['quantity']))
        for i in range(depth):
            offers['ask_price'].append(float(bittrex_response['ask'][i]['rate']))
        for i in range(depth):
            offers['ask_amount'].append(float(bittrex_response['ask'][i]['quantity']))
    return offers


def search_offers_bitbay(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    bitbay_response = connect_with_api(BITBAY_ORDERBOOK + currency + BITBAY_ORDER)

    if bitbay_response:
        for i in range(depth):
            offers['bid_price'].append(bitbay_response['bids'][i][0])
        for i in range(depth):
            offers['bid_amount'].append(bitbay_response['bids'][i][1])
        for i in range(depth):
            offers['ask_price'].append(bitbay_response['asks'][i][0])
        for i in range(depth):
            offers['ask_amount'].append(bitbay_response['asks'][i][1])
    return offers


def arbitrage(currency, ask, bid, ask_taker_fee, bid_taker_fee, ask_transfer_fee):
    depth = 0
    i = 0
    j = 0
    arbitrages = []

    while depth < DEPTH:
        transaction_volume = min(ask['ask_amount'][i], bid['bid_amount'][j])

        buy = ask['ask_price'][i] * transaction_volume
        sell = bid['bid_price'][j] * transaction_volume
        buy_fee = buy * ask_taker_fee + ask_transfer_fee * ask['ask_price'][i]
        sell_fee = sell * bid_taker_fee
        total_fee = buy_fee + sell_fee
        profit = sell - buy - total_fee

        arbitrages.append(profit)

        i += 1
        j += 1
        depth += 1

    max = arbitrages[0]
    for elem in arbitrages:
        if elem > max:
            max = elem

    return max


def sample_currencies():
    SAMPLE_CURRENCIES = ["BAT-USD", "BTC-USD", "GAME-BTC"]

    for i in SAMPLE_CURRENCIES:
        bitbay_offers = search_offers_bitbay(i)
        bittrex_offers = search_offers_bittrex(i)
        currency = i.split('-')
        bittrex_to_bitbay = arbitrage(currency[0], bittrex_offers, bitbay_offers,
                                      BITTREX_TAKER_FEE, BITBAY_TAKER_FEE, bittrex_transfer_fees[currency[0]])
        bitbay_to_bittrex = arbitrage(currency[0], bitbay_offers, bittrex_offers,
                                      BITBAY_TAKER_FEE, BITTREX_TAKER_FEE, bitbay_transfer_fees[currency[0]])
        if bitbay_to_bittrex > bittrex_to_bitbay:
            direction = 'bitbayToBittrex'
            profit = bitbay_to_bittrex
        else:
            direction = 'bittrexToBitbay'
            profit = bittrex_to_bitbay
        result = [profit, i, direction]
        print(result)


def all_currencies(common_currencies):
    ranking = []

    for i in common_currencies:
        bitbay_offers = search_offers_bitbay(i)
        bittrex_offers = search_offers_bittrex(i)
        currency = i.split('-')
        bittrex_to_bitbay = arbitrage(currency[0], bittrex_offers, bitbay_offers,
                                      BITTREX_TAKER_FEE, BITBAY_TAKER_FEE, bittrex_transfer_fees[currency[0]])
        bitbay_to_bittrex = arbitrage(currency[0], bitbay_offers, bittrex_offers,
                                      BITBAY_TAKER_FEE, BITTREX_TAKER_FEE, bitbay_transfer_fees[currency[0]])
        if bitbay_to_bittrex > bittrex_to_bitbay:
            direction = 'bitbayToBittrex'
            profit = bitbay_to_bittrex
        else:
            direction = 'bittrexToBitbay'
            profit = bittrex_to_bitbay
        result = profit, i, direction
        ranking.append(result)

    ranking = sorted(ranking, key=lambda tup: tup[0], reverse=True)

    for i in ranking:
        print(i)


if __name__ == '__main__':
    response_bitbay = get_bitbay_data(connect_with_api(BITBAY_MARKETS))
    response_bittrex = get_bittrex_data(connect_with_api(BITTREX_MARKETS))

    print("Common currencies for bitbay and bittrex: ")
    common_currencies = get_common_markets(response_bitbay, response_bittrex)
    print(common_currencies)

    # sample_currencies()

    while True:
        print("ranking: ")
        all_currencies(common_currencies)

        time.sleep(DELAY)
