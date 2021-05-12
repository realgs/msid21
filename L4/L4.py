import requests
import time
import Bittrex
import Bitbay

TIME_TO_WAIT = 5
BASE_CURRENCY = "USD"
ARRAY = ["BTC", "LTC", "ETH"]
FEES_BITBAY = [0.0005, 0.001, 0.01]
FEES_BITTREX = [0.0005, 0.01, 0.006]
BITREX_TAKER = 0.0025
BITBAY_TAKER = 0.0043

def compute(buy: float, sell: float):
    return (1 - ((sell - buy)/buy))

def getData(link: str):
    response = requests.get(link)
    if 200 <= response.status_code <= 299:
        return response
    else: return None

def findBest(r1, r2, nrOfCurrency):
    transferFeeBittrex=FEES_BITTREX[nrOfCurrency]
    transferFeeBitbay = FEES_BITBAY[nrOfCurrency]
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

while True:
    responses1 = Bitbay.connect()
    responses2 = Bittrex.connect()
    i = 0
    while i < 3:
        print(str(MARKETS[i]).split("-")[0])
        j = 0
        while j < 3:
            print("Difference in bids: ", abs(1 - compute(Bitbay.getField(responses1[i].json(), j, "bids")[0], Bittrex.getField(responses2[i].json(), j, "bids")[0])))
            print("Difference in asks: ", abs(1 - compute(Bitbay.getField(responses1[i].json(), j, "asks")[0],
                                          Bittrex.getField(responses2[i].json(), j, "asks")[0])))
            findBest(responses1[i], responses2[i], i)
            j += 1
        i += 1
        print("- - - - - - - - - - - -")
        time.sleep(1)
    time.sleep(TIME_TO_WAIT)
    print("-----------------------------------")


