import requests

SLEEP = 5
APIS = {"bitbay": {"orderbook": "https://bitbay.net/API/Public/{}/orderbook.json",
                   "markets": "https://api.bitbay.net/rest/trading/ticker"},
         "bittrex": {"orderbook": "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both",
                    "markets": "https://api.bittrex.com/v3/markets"}
         }

FEES = {"bitbay":
                   {"taker_fee": 0.0042,
                        "transfer_fee": {"AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0, "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1, "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0, "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0, "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0}},
        "bittrex":
                    {"taker_fee": 0.0075,
                         "transfer_fee": {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5, 'EOS': 0.1, 'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25}}
        }

def getMarkets(api):
    markets = []
    try:
        if api == "bitbay":
            req = requests.get(APIS[api]['markets'])
            if req.status_code in range(200, 299):
                req = req.json()
                for i in req['items'].keys():
                    markets.append(i)
                return markets
            else:
                return None
        elif api == "bittrex":
            req = requests.get(APIS[api]['markets'])
            if req.status_code in range(200, 299):
                req = req.json()
                for i in range(0, len(req)):
                    markets.append(req[i]['symbol'])
                return markets
    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None

def getSharedCurr(api1, api2):
    shared = []
    for i in api1:
        if i in api2:
            shared.append(i)
    return shared

def getOffers(api, crypto, curr):
    try:
        if api == "bitbay":
            offers = requests.get(APIS[api]['orderbook'].format(crypto + curr))
            if offers.status_code in range(200,299):
                return offers.json()
        if api == "bittrex":
            offers = requests.get(APIS[api]["orderbook"].format(curr, crypto))
            if offers.status_code in range(200, 299):
                return offers.json()
        else:
            return None

    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None

def countBidFee(bid, fees, curr):
    return bid * (1 - fees['taker_fee'])

def countAskFee(ask, fees, curr):
    return ask * (1 + fees['taker_fee']) + fees['transfer_fee'][curr]


def arbitrage(api, api2, curr, curr2):
    bidsBitbay = api['bids']
    bidsBittrex = api2['result']['buy']
    asksBitbay = api['asks']
    asksBittrex = api2['result']['sell']

    i = 0
    j = 0
    profit = 0
    place = ""
    while countBidFee(bidsBittrex[i]['Rate'], FEES['bittrex'], curr) > countAskFee(asksBitbay[j][0],
                                                                                   FEES['bitbay'], curr):
        place = "bitbay"
        amount = min(asksBitbay[i][1], bidsBittrex[i]['Quantity'])
        profit += (countBidFee(bidsBittrex[i]['Rate'], FEES['bittrex'], curr) -
                   countAskFee(asksBitbay[j][0], FEES['bitbay'], curr)) * amount
        arr('bittrex', 'bitbay', bidsBittrex[i]['Quantity'], asksBitbay[i][1], i, j)

    while countBidFee(bidsBitbay[i][0], FEES['bitbay'], curr) > countAskFee(asksBittrex[j]['Rate'],
                                                                            FEES['bittrex'], curr):
        place = "bittrex"
        amount = min(asksBittrex[i]['Quantity'], bidsBitbay[i][1])
        profit += (countBidFee(bidsBitbay[i][0], FEES['bitbay'], curr) - countAskFee(asksBittrex[j]['Rate'],
                                                                                     FEES['bittrex'], curr)) * amount
        arr('bitbay', 'bittrex', bidsBitbay[i][1], asksBittrex[i]['Quantity'], i, j)

    return curr + curr2, place, profit, curr


def arr(api, api2, bids, asks, i, j):
    if api == 'bitbay' and api2 == 'bittrex':
        if asks[i]['Quantity'] == bids[i][1]:
            i += 1
            j += 1
        if asks[i]['Quantity'] < bids[i][1]:
            j += 1
            bids[i][1] = bids[i][1] - bids[i]['Quantity']
        if asks[i]['Quantity'] > bids[i][1]:
            i += 1
            bids[i][1] = bids[i][1] - asks[i]['Quantity']

    elif api == 'bittrex' and api2 == 'bitbay':
        if asks[i][1] == bids[i]['Quantity']:
            i += 1
            j += 1
        if asks[i][1] < bids[i]['Quantity']:
            j += 1
            bids[i]['Quantity'] = bids[i]['Quantity'] - asks[i][1]
        if asks[i][1] > bids[i]['Quantity']:
            i += 1
            asks[i][1] = asks[i][1] - bids[i]['Quantity']

def checkArbitrage(curr, curr2):
    bitbayData = getMarkets("bitbay")
    bittrexData = getMarkets("bittrex")
    common_curr = getSharedCurr(bitbayData, bittrexData)
    if curr + "-" + curr2 in common_curr:
        currencies = (curr+"-"+curr2).split('-')
        bitbayOffer = getOffers("bitbay", currencies[0], currencies[1])
        bittrexOffer = getOffers("bittrex", currencies[0], currencies[1])
        return arbitrage(bitbayOffer, bittrexOffer, currencies[0], curr2)
    return "No arbitrage"