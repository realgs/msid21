import requests
import time
import Bittrex
import Bitbay

TIME_TO_WAIT = 5

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

BITTREX_FEES = {}

BITREX_TAKER = 0.0025
BITBAY_TAKER = 0.0043

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def getData(link: str):
    response = requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def getBittrexFees():
    return requests.get("https://api.bittrex.com/api/v1.1/public/getcurrencies").json()["result"]

def createBittrexFees():
    l = getBittrexFees()
    for item in l:
        BITTREX_FEES[item['Currency']] = item['TxFee']

createBittrexFees()

def findBest(r1, r2, curr):
    transferFeeBittrex=BITTREX_FEES[curr]
    transferFeeBitbay = BITBAY_FEES[curr]
    amountToBeArbitrated = 0.0
    inplus = False
    i = 0
    diff = 0
    computedDiff=diff
    while i < 3:
        j = 0
        while j < Bitbay.getOrdersNumber(r1.json()) and j < Bittrex.getOrdersNumber(r2.json()):
            buyOnBitbay = Bitbay.getField(r1.json(), i, "sells")[0] * Bitbay.getField(r1.json(), i, "sells")[1] - (Bitbay.getField(r1.json(), i, "sells")[0] * Bitbay.getField(r1.json(), i, "sells")[1] * BITBAY_TAKER) - (Bitbay.getField(r1.json(), i, "sells")[0] * Bitbay.getField(r1.json(), i, "sells")[1] * transferFeeBitbay)
            buyOnBittrex = Bittrex.getField(r2.json(), i, "sells")[0] * Bittrex.getField(r2.json(), i, "sells")[1] - (Bittrex.getField(r2.json(), i, "sells")[0] * Bittrex.getField(r2.json(), i, "sells")[1] * BITREX_TAKER) - (Bitbay.getField(r1.json(), i, "sells")[0] * Bitbay.getField(r1.json(), i, "sells")[1] * transferFeeBittrex)
            sellOnBitbay = Bitbay.getField(r1.json(), j, "bids")[0] * Bitbay.getField(r1.json(), j, "bids")[1] - (Bitbay.getField(r1.json(), j, "bids")[0] * Bitbay.getField(r1.json(), j, "bids")[1] * BITBAY_TAKER) - (Bitbay.getField(r1.json(), j, "bids")[0] * Bitbay.getField(r1.json(), j, "bids")[1] * transferFeeBitbay)
            sellOnBittrex = Bittrex.getField(r2.json(), j, "bids")[0] * Bittrex.getField(r2.json(), j, "bids")[1] - (Bittrex.getField(r2.json(), j, "bids")[0] * Bittrex.getField(r2.json(), j, "bids")[1] * BITREX_TAKER) - (Bittrex.getField(r2.json(), j, "bids")[0] * Bittrex.getField(r2.json(), j, "bids")[1] * transferFeeBittrex)
            if Bitbay.getField(r1.json(), i, "sells")[1] > Bittrex.getField(r2.json(), j, "bids")[1]:
                computedDiff = sellOnBittrex - buyOnBitbay
            if computedDiff > diff:
                amountToBeArbitrated = Bittrex.getField(r2.json(), j, "bids")[1]
                diff = computedDiff
                inplus = True
            if Bittrex.getField(r2.json(), i, "sells")[1] > Bitbay.getField(r1.json(), j, "bids")[1]:
                computedDiff = sellOnBitbay - buyOnBittrex
            if computedDiff > diff:
                amountToBeArbitrated = Bitbay.getField(r1.json(), j, "bids")[1]
                diff = computedDiff
                inplus = True
            j += 1
        i += 1
    if inplus:
        print("Can be arbitrated: ", amountToBeArbitrated)
        print("Profit: ", diff)

def commonMarkets():
    Bittrex.getAllMarkets()
    Bitbay.getAllMarkets()
    return Bitbay.markets.intersection(Bittrex.markets)

MARKETS = list(commonMarkets())

def getMarkets():
    return MARKETS

while True:
    Bitbay.MARKETS = MARKETS
    Bittrex.MARKETS = MARKETS
    responses1 = Bitbay.connect()
    responses2 = Bittrex.connect()
    i = 0
    while i < 3:
        print(str(MARKETS[i]).split("-"))
        j = 0
        while j < 3:
            print("Difference in bids: ", abs(1 - compute(Bitbay.getField(responses1[i].json(), j, "bids")[0], Bittrex.getField(responses2[i].json(), j, "bids")[0])))
            print("Difference in asks: ", abs(1 - compute(Bitbay.getField(responses1[i].json(), j, "asks")[0],
                                          Bittrex.getField(responses2[i].json(), j, "asks")[0])))
            findBest(responses1[i], responses2[i], str(MARKETS[i]).split("-")[0])
            j += 1
        i += 1
        print("- - - - - - - - - - - -")
        time.sleep(1)
    time.sleep(TIME_TO_WAIT)
    print("-----------------------------------")


