import requests

APIS = {"bitbay": {
                   "fees":
                       {"taker_fee": 0.0042,
                        "transfer_fee": {"AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0, "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1, "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0, "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0, "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0}}},
        "bittrex": {
                    "fees":
                        {"taker_fee": 0.0075,
                         "transfer_fee": {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5, 'EOS': 0.1, 'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25}}}}
def getBids(api, curr1, curr2):
    try:
        if api == "bitbay":
            offers = requests.get("https://bitbay.net/API/Public/{}/orderbook.json".format(curr1 + curr2))
            try:
                if 199 < offers.status_code < 300:
                    offer = offers.json()
                    return offer['bids']
                else:
                    print("Response error")
                    return None
            except KeyError:
                return None
        if api == "bittrex":
            offers = requests.get("https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(curr2, curr1))
            try:
                if 199 < offers.status_code < 300:
                    offer = offers.json()
                    return offer['result']['buy']
                else:
                    print("Response error")
                    return None
            except TypeError:
                return None
    except requests.exceptions.ConnectionError:
        print("Connection error")
        return None

def countFee(bid, fees, curr):
    return bid * (1 - fees['taker_fee']) - fees['transfer_fee'][curr]

def countProfit(api, fees, bids, curr, quantity):
    try:
        i = 0
        value = 0
        while quantity > 0:
            if bids[i][1] > quantity:
                value += countFee(bids[i][0], APIS[api][fees], curr) * quantity
                quantity = 0
            else:
                value += countFee(bids[i][0], APIS[api][fees], curr) * bids[i][1]
                quantity -= bids[i][1]
            i += 1

        return value
    except TypeError:
        return None

def calculateValue(currency, baseCurrency, quantity, percent=100):
    try:
        part = None
        bidsBitbay = getBids("bitbay", currency, baseCurrency)
        bidsBittrex = getBids("bittrex", currency, baseCurrency)
        profit = max(countProfit("bitbay", "fees", bidsBitbay, currency, quantity), countProfit("bittrex", "fees", bidsBitbay, currency, quantity))
        if percent != 100:
            part = max(countProfit("bitbay", "fees", bidsBitbay, currency, quantity * percent/100),
                       countProfit("bittrex", "fees", bidsBitbay, currency, quantity * percent/100))
        if profit == countProfit("bitbay", "fees", bidsBitbay, currency, quantity):
            return round(profit,3), bidsBitbay[0][0], part, "bitbay"
        return round(profit), bidsBittrex[0][0], part, "bittrex"
    except TypeError:
        return None
