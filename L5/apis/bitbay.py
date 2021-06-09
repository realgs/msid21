import requests

API = "https://bitbay.net/API/Public/{}{}/orderbook.json"
BITBAY_TAKER = 0.0043
BITBAY_FEES = {
    'AAVE'	:	0.54000000,
    'ALG'	:	426.00000000,
    'AMLT'	:	1743.00000000,
    'BAT'	:	156.00000000,
    'BCC'	:	0.00100000,
    'BCP'	:	1237.00000000,
    'BOB'	:	11645.00000000,
    'BSV'	:	0.00300000,
    'BTC'	:	0.00050000,
    'BTG'	:	0.00100000,
    'COMP'	:	0.10000000,
    'DAI'	:	81.00000000,
    'DASH'	:	0.00100000,
    'DOT'	:	0.10000000,
    'EOS'	:	0.1000,
    'ETH'	:	0.00600000,
    'EXY'	:	520.00000000,
    'GAME'	:	479.00000000,
    'GGC'	:	112.00000000,
    'GNT'	:	403.00000000,
    'GRT'	:	84.00000000,
    'LINK'	:	2.70000000,
    'LML'	:	1500.00000000,
    'LSK'	:	0.30000000,
    'LTC'	:	0.00100000,
    'LUNA'	:	0.02000000,
    'MANA'	:	100.00000000,
    'MKR'	:	0.02500000,
    'NEU'	:	572.00000000,
    'NPXS'	:	46451.00000000,
    'OMG'	:	14.00000000,
    'PAY'	:	1523.00000000,
    'QARK'	:	1019.00000000,
    'REP'	:	3.20000000,
    'SRN'	:	5717.00000000,
    'SUSHI'	:	8.80000000,
    'TRX'	:	1.000000,
    'UNI'	:	2.50000000,
    'USDC'	:	125.000000,
    'USDT'	:	190.00000000,
    'XBX'	:	5508.00000000,
    'XIN'	:	5.00000000,
    'XLM'	:	0.0050000,
    'XRP'	:	0.100000,
    'XTZ'	:	0.100000,
    'ZEC'	:	0.00400000,
    'ZRX'	:	56.00000000
}

class Bitbay():

    def __init__(self):
        pass

    def getSellRate(self, crypto):
        response = requests.get(API.format(crypto, "USD"))
        if(response.status_code == 200):
            offers = response.json()["bids"]
            if(len(offers) > 0):
                return float(offers[0][0])
            else:
                return -1
        else:
            return -1

    def sellCrypto(self, crypto, rate, volume):
        response = requests.get(API.format(crypto, "USD"))
        sumValue = rate * volume
        sellValue = 0
        if(response.status_code == 200):
            offers = response.json()["bids"]
            index = 0
            sum = 0
            while volume > 0 and index < len(offers):
                if volume > offers[index][1]:
                    sellValue += offers[index][0] * offers[index][1]
                    volume -= offers[index][1]
                else:
                    sellValue += offers[index][0] * volume
                index += 1
            return sellValue
        else:
            return None

    def getOrdersNumber(self, json):
        l1 = len(json["bids"])
        l2 = len(json["asks"])
        if l1 > l2:
            return l2
        else:
            return l1

    def getField(self, json, i, action):
        if action == "asks":
            return (json["asks"][i][0], json["asks"][i][1])
        else:
            return (json["bids"][i][0], json["bids"][i][1])

    def getOrderBook(self, crypto):
        s = "https://bitbay.net/API/Public/{}{}/orderbook.json".format(crypto, "USD")
        return requests.get(s)
