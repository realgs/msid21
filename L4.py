import requests
import time

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
SAMPLE_CURRENCIES = ["LTC-USD", "BTC-USD", "BSV-BTC"]

def getMarketsBitbay(api):                                    #get all markets from given api
    markets = []
    try:
        req = requests.get(APIS[api]['markets'])
        if req.status_code in range(200, 299):
            req = req.json()
            for i in req['items'].keys():
                markets.append(i)
            return markets
        else:
            return None

    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None

def getMarketsBittrex(api):                                    #get all markets from given api
    markets = []
    try:
        req = requests.get(APIS[api]['markets'])
        if req.status_code in range(200, 299):
            req = req.json()
            for i in range(0, len(req)):
                markets.append(req[i]['symbol'])
            return markets
        else:
            return None

    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None

def getSharedCurr(api1, api2):                          #get shared curriences from both apis
    shared = []
    for i in api1:
        if i in api2:
            shared.append(i)
    return shared

def getOffersBitbay(api, crypto, curr):                                           #get all currency offerts from given api
    try:
        if api == "bitbay":
            offers = requests.get(APIS[api]['orderbook'].format(crypto + curr))
            if offers.status_code in range(200,299):
                return offers.json()
        else:
            return None

    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None

def getOffersBittrex(api, crypto, curr):                                           #get all currency offerts from given api
    try:
        if api == "bittrex":
            offers = requests.get(APIS[api]["orderbook"].format(curr, crypto))
            if offers.status_code in range(200,299):
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

def sampleCurrencies():                                                        #exercise 2
    for i in SAMPLE_CURRENCIES:
        currencies = i.split('-')
        offer1 = getOffersBitbay("bitbay", currencies[0], currencies[1])
        offer2 = getOffersBittrex("bittrex", currencies[0], currencies[1])
        arb = arbitrage(offer1, offer2, currencies[0])
        if arb <= 0:
            print("No arbitrage")
        else:
            print("Profit in {} ".format(currencies[1]) + str(arb))


def arbitrage(bitbay, bittrex, curr):

    bitbayBid = bitbay['bids']
    bittrexBid = bittrex['result']['buy']
    bitbayAsk = bitbay['asks']
    bittrexAsk = bittrex['result']['sell']

    i = 0
    j = 0
    amount = 0
    profit = 0

    while countBidFee(bittrexBid[i]['Rate'], FEES['bittrex'], curr) > countAskFee(bitbayAsk[j][0], FEES['bitbay'], curr):           #buy at bittrex sell bitbay
           amount = min(bitbayAsk[i][1], bittrexBid[j]['Quantity'])
           profit += (countBidFee(bittrexBid[i]['Rate'], FEES['bittrex'], curr) - countAskFee(bitbayAsk[j][0], FEES['bitbay'], curr)) * amount
           if bitbayAsk[i][1] == bittrexBid[j]['Quantity']:
               i += 1
               j += 1
           if bitbayAsk[i][1] < bittrexBid[j]['Quantity']:
               j += 1
               bittrexBid[j]['Quantity'] = bittrexBid[j]['Quantity'] - bitbayAsk[i][1]
           if bitbayAsk[i][1] > bittrexBid[j]['Quantity']:
               i += 1
               bitbayAsk[i][1] = bitbayAsk[j][1] - bittrexBid[i]['Quantity']
    i = 0
    j = 0 

    while countBidFee(bitbayBid[i][0], FEES['bitbay'], curr) > countAskFee(bittrexAsk[j]['Rate'], FEES['bittrex'], curr):           #buy at bitbay sell at bittrex
            amount = min(bittrexAsk[i]['Quantity'], bitbayBid[j][1])
            profit += (countBidFee(bitbayBid[i][0], FEES['bitbay'], curr) - countAskFee(bittrexAsk[j]['Rate'], FEES['bittrex'], curr)) * amount
            if bittrexAsk[j]['Quantity'] == bitbayBid[i][1]:
                i += 1
                j += 1
            if bittrexAsk[j]['Quantity'] < bitbayBid[i][1]:
                j += 1
                bitbayBid[i][1] = bitbayBid[i][1] - bittrexAsk[j]['Quantity']
            if bittrexAsk[j]['Quantity'] > bitbayBid[i][1]:
                i += 1
                bitbayBid[i][1] = bitbayBid[i][1] - bittrexAsk[j]['Quantity']

    if profit == 0:
        profit = max(countBidFee(bitbayBid[0][0], FEES['bitbay'], curr) - countAskFee(bittrexAsk[0]['Rate'], FEES['bittrex'], curr), \
           countBidFee(bittrexBid[0]['Rate'], FEES['bittrex'], curr) - countAskFee(bitbayAsk[0][0], FEES['bitbay'], curr))
    
    return profit


if __name__ == '__main__':

    #while True:
        bitbayData = getMarketsBitbay("bitbay")
        bittrexData = getMarketsBittrex("bittrex")
        common_curr = getSharedCurr(bitbayData, bittrexData)

        ranking = []
        sampleCurrencies()

        for curr in common_curr:
            currencies = curr.split('-')
            bitbayOffer = getOffersBitbay("bitbay", currencies[0], currencies[1])
            bittrexOffer = getOffersBittrex("bittrex", currencies[0], currencies[1])

            ranking.append((curr, arbitrage(bitbayOffer, bittrexOffer, currencies[0])))

        ranking = sorted(ranking, key=lambda tuple: tuple[1], reverse=True)

        for i in ranking:
            print(i)
        #time.sleep(SLEEP)


