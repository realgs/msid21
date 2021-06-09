import requests

APIS = {"bitbay": {"orderbook": "https://bitbay.net/API/Public/{}/orderbook.json",
                   "fees":
                       {"taker_fee": 0.0042,
                        "transfer_fee": {"AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0, "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1, "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0, "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0, "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0}}}}


def get_bids(api_name, curr1, curr2):
    try:
        if api_name == "bitbay":
            offers = requests.get(APIS[api_name]['orderbook'].format(curr1 + curr2))
            if 199 < offers.status_code < 300:
                offer = offers.json()
                return offer['bids']
        else:
            return None
    except requests.exceptions:
        return None


def bid_with_fees(bid, fees, curr):
    return bid * (1 - fees['taker_fee']) - fees['transfer_fee'][curr]


def get_value(api_name, fees, bids, curr, owned_quantity):
    i = 0
    value = 0

    while owned_quantity > 0:
        if bids[i][1] > owned_quantity:
            quantity = owned_quantity
        else:
            quantity = bids[i][1]

        value += bid_with_fees(bids[i][0], APIS[api_name][fees], curr) * quantity
        owned_quantity -= quantity

        i += 1
    return value


def calculate_value(currency, base_currency, quantity, percent=100):
    partial_value = None
    bids = get_bids("bitbay", currency, base_currency)
    value = get_value("bitbay", "fees", bids, currency, quantity)
    if percent != 100:
        partial_value = get_value("bitbay", "fees", bids, currency, quantity * percent/100)
    return value, bids[0][0], partial_value


if __name__ == '__main__':
    # mini test:
    print(calculate_value("BTC", "USD", 0.5))
    print(calculate_value("BTC", "USD", 0.5, percent=30))
