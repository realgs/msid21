import time
import requests

CRYPTO = "BTC"
CURR = "USD"
API1 = "https://bitbay.net/API/Public/{}{}/orderbook.json".format(CRYPTO, CURR)
API2 = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(CURR, CRYPTO)
API1_FEES = {"taker": 0.0042, "currFee": 0.0005}
API2_FEES = {"taker": 0.0025, "currFee": 0.0005}
SLEEP = 5

def getData(api):                                                   #acquire data from api
    try:
        req = requests.get(api)
        if req.status_code in range(200, 299):
            return req.json()
        else:
           return None
    except requests.exceptions.ConnectionError:
        print("Error with connecting")
        return None
    except:
        print("Unexpected error")
        return None


def getBidBitbay(bid):                                              #get bid cost and amount from BitBay
    bids = bid['bids']
    return bids[0][0], bids[0][1]

def getBidBittrex(bid):                                             #get bid cost and amount from Bittrex
    bids = bid['result']['buy']
    return bids[0]['Rate'], bids[0]['Quantity']

def getAskBitbay(ask):                                              #get ask cost and amount from Bitbay
    asks = ask['asks']
    return asks[0][0], asks[0][1]

def getAskBittrex(ask):                                             #get ask cost and amount from Bittrex
    asks = ask['result']['sell']
    return asks[0]['Rate'], asks[0]['Quantity']

def printDiff(bitbayBid, bittrexBid, bitbayAsk, bittrexAsk):        #print diffrence in percentage beetwen bids and asks and buying/selling
    print("\nBuying diffrence (bitbay/bittrex):")
    print((bitbayBid / bittrexBid) - 1, "%\n")
    print("Selling diffrence (bitbay/bittrex):")
    print((bitbayAsk / bittrexAsk) - 1, "%\n")
    print("Buying on bittrex selling on bitbay (no fees):")
    print((bitbayBid / bittrexAsk) - 1, "%\n")
    print("Buying on bitbay selling on bittrex (no fees):")
    print((bittrexBid / bitbayAsk) - 1, "%\n")

def countBidFee(bid, fee):                                          #count cost after fees
    return bid * (1 - fee['taker'])

def countAskFee(ask, fee):                                          #count cost after fees
    return ask * (1 + fee['taker'] + fee['currFee'])

def getBidsAsks(offer, offer2):                                      #get bids and asks from each site
    bitbayBids = getBidBitbay(offer)
    bittrexBids = getBidBittrex(offer2)
    bitbayAsks = getAskBitbay(offer)
    bittrexAsks = getAskBittrex(offer2)
    return bitbayBids, bittrexBids, bitbayAsks, bittrexAsks

def countAllFees(bids1, bids2, asks1, asks2):                       #calculate all fees
    bidFromBitbay = countBidFee(bids1[0], API1_FEES)
    bidFromBittrex = countBidFee(bids2[0], API2_FEES)
    askFromBitbay = countBidFee(asks1[0], API1_FEES)
    askFromBittrex = countBidFee(asks2[0], API2_FEES)
    return bidFromBitbay, bidFromBittrex, askFromBitbay, askFromBittrex


def checkArbitrage(bitbayBid, bittrexBid, bitbayAsk, bittrexAsk):           #check if arbitrage has place and print data about volumen, arbitrage value
    fees = countAllFees(bitbayBid, bittrexBid, bitbayAsk, bittrexAsk)
    print("Arbitrage when buying at bittrex and selling at bitbay: ")
    if(fees[0] > fees[3]):
        amount = min(bitbayBid[1], bittrexAsk[1])
        profit = (fees[0] - fees[3]) * amount
        print("Volumen: ", amount)
        print("Profit in %: ", 100 * profit / fees[3], "%")
        print("Profit in USD: ", profit)
    else:
        print("Arbitrage has no place at the moment")

    print("\nArbitrage when buying at bitbay and selling at bittrex: ")
    if(fees[1] > fees[2]):
        amount = min(bittrexBid[1], bitbayAsk[1])
        profit = (fees[1] - fees[2]) * amount
        print("Volumen: ", amount)
        print("Profit in %: ", 100 * profit / fees[2], "%")
        print("Profit in USD: ", profit)
    else:
        print("Arbitrage has no place at the moment")

def printOffers(offers, offers2):                           #print offers (helper in checking if arbitrage counts well)
    allOffers = getBidsAsks(offers, offers2)
    print("Bids offers from Bitbay: ", allOffers[0])
    print("Bids offers from Bittrex: ", allOffers[1])
    print("Asks offers from Bitbay: ", allOffers[2])
    print("Asks offers from Bittrex: ", allOffers[3])

if __name__ == '__main__':
    offers = getData(API1)
    offers2 = getData(API2)
    allOffers = getBidsAsks(offers, offers2)
    while True:
        printOffers(offers, offers2)
        printDiff(allOffers[0][0], allOffers[1][0], allOffers[2][0], allOffers[3][0])
        checkArbitrage(allOffers[0], allOffers[1], allOffers[2], allOffers[3])
        print()
        time.sleep(SLEEP)
