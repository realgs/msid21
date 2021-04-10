import requests
import time
import Bittrex
import Bitbay

TIME_TO_WAIT = 5
CURRENCY = "USD"
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
    print(transferFeeBittrex)
    print(transferFeeBitbay)
    print("- - - - - - - - - - - -")
    boolean = False
    i = 0
    diff = -1000
    computedDiff=0
    while i < 3:
        j = 0
        while j < 3:
            buyOnBitbay = Bitbay.getField(r1.json(), j, "sells")[0] * Bitbay.getField(r1.json(), j, "sells")[1] - (Bitbay.getField(r1.json(), j, "sells")[0] * Bitbay.getField(r1.json(), j, "sells")[1] * BITBAY_TAKER)
            buyOnBittrex = Bittrex.getField(r2.json(), j, "sells")[0] * Bittrex.getField(r2.json(), j, "sells")[1] - (Bittrex.getField(r2.json(), j, "sells")[0] * Bittrex.getField(r2.json(), j, "sells")[1] * BITREX_TAKER)
            sellOnBitbay = Bitbay.getField(r1.json(), j, "bids")[0] * Bitbay.getField(r1.json(), j, "bids")[1] - (Bitbay.getField(r1.json(), j, "bids")[0] * Bitbay.getField(r1.json(), j, "bids")[1] * BITBAY_TAKER)
            sellOnBittrex = Bittrex.getField(r2.json(), j, "bids")[0] * Bittrex.getField(r2.json(), j, "bids")[1] - (Bittrex.getField(r2.json(), j, "bids")[0] * Bittrex.getField(r2.json(), j, "bids")[1] * BITREX_TAKER)
            if Bitbay.getField(r1.json(), j, "sells")[1] > Bittrex.getField(r2.json(), j, "bids")[1]:
                computedDiff = (buyOnBitbay - sellOnBittrex) - ((buyOnBitbay - sellOnBittrex) * transferFeeBittrex) - ((buyOnBitbay - sellOnBittrex) * transferFeeBitbay)
            if computedDiff < buyOnBittrex - sellOnBitbay and Bitbay.getField(r1.json(), j, "sells")[1] < Bittrex.getField(r2.json(), j, "bids")[1]:
                computedDiff = (buyOnBittrex - sellOnBitbay) - ((buyOnBittrex - sellOnBitbay) * transferFeeBittrex) - ((buyOnBittrex - sellOnBitbay) * transferFeeBitbay)
            if computedDiff > diff:
                diff=computedDiff
                boolean = True
            j += 1
        i += 1
    if boolean:
        print("Profit: ", diff)


while True:
    responses1 = Bitbay.connect()
    responses2 = Bittrex.connect()
    i = 0
    while i < 3:
        print(ARRAY[i])
        j = 0
        while j < 3:
            print("Difference in bids: ", abs(1-compute(Bitbay.getField(responses1[i].json(), j, "bids")[0], Bittrex.getField(responses2[i].json(), j, "bids")[0])))
            print("Difference in asks: ", abs(1-compute(Bitbay.getField(responses1[i].json(), j, "asks")[0],
                                          Bittrex.getField(responses2[i].json(), j, "asks")[0])))
            findBest(responses1[i], responses2[i], i)
            j += 1
        i += 1
        time.sleep(1)
    time.sleep(TIME_TO_WAIT)

update()