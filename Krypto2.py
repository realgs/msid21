import requests
import time

BITTREX_LINK_START = "https://api.bittrex.com/api/v1.1/public/getorderbook?market="
BITTREX_LINK_END = "&type=both"
BITTREX_FEES = {
    'taker': 0.0035,
    'transfer': { 'BTC': 0.0005, 'ETH': 0.006 , 'USD': 0 }
}
BITBAY_LINK_START = "https://bitbay.net/API/Public/"
BITBAY_LINK_END = "/orderbook.json"
BITBAY_FEES = {
    'taker': 0.0042,
    'transfer': { 'BTC': 0.0005, 'ETH': 0.01 , 'USD': 3 }
}

CURRENCIES = {'dolar': 'USD', 'bitcoin': 'BTC', 'ethereum': 'ETH'}
printDelay = 5

# [currency, crypto,  [ bidPrice, ammountOfBidPrice, askPrice, ammountOfAskPrice ], ... ]
def downloadData(currencyToBuy, currency):
    data = {'currency': currency, 'currencyToBuy': currencyToBuy}
    try:
        infoPack = requests.get(BITTREX_LINK_START + currency + "-" + currencyToBuy + BITTREX_LINK_END).json()
        data['bittrexBidPrice'] = infoPack['result']['buy'][0]['Rate']
        data['bittrexBidAmmount'] = infoPack['result']['buy'][0]['Quantity']
        data['bittrexAskPrice'] = infoPack['result']['sell'][0]['Rate']
        data['bittrexAskAmmount'] = infoPack['result']['sell'][0]['Quantity']
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to BitTrex API + " + infoPack.reason)
        return None

    try:
        infoPack = requests.get(BITBAY_LINK_START + currencyToBuy + currency + BITBAY_LINK_END).json()
        data['bitbayBidPrice'] = infoPack['bids'][0][0]
        data['bitbayBidAmmount'] = infoPack['bids'][0][1]
        data['bitbayAskPrice'] = infoPack['asks'][1][0]
        data['bitbayAskAmmount'] = infoPack['asks'][1][1]
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to BitBay API + " + infoPack.reason)
        return None

    return data

def calculatePercentDifferecne(price1, price2):
    return (price1-price2)/price2*100

def printPriceDifference(data):
    print("BID price difference: " + str(abs(calculatePercentDifferecne(data['bittrexBidPrice'], data['bitbayBidPrice']))) + "%")
    print("ASK price difference: " + str(abs(calculatePercentDifferecne(data['bittrexAskPrice'], data['bitbayAskPrice']))) + "%")
    print()
    print("BUY in BITTREX, SELL in BITBAY: " + str(calculatePercentDifferecne(data['bitbayBidPrice'], data['bittrexAskPrice'])) + "%")
    print("BUY in BITBAY, SELL in BITTREX: " + str(calculatePercentDifferecne(data['bittrexBidPrice'], data['bitbayAskPrice'])) + "%")
    print()
    #print("Bittrex Bid Price " + str(data['bittrexBidPrice']))
    #print("Bittrex Ask Price " + str(data['bittrexAskPrice']))
    #print("Bitbay Bid Price " + str(data['bitbayBidPrice']))
    #print("Bitbay Ask Price " + str(data['bitbayAskPrice']))


def calculateProfit(data):
    trexBayAmmount = min(data['bitbayBidAmmount'], data['bittrexAskAmmount'])
    trexBayBuyCost = trexBayAmmount * data['bittrexAskPrice']
    trexBayAmmount = ((trexBayAmmount * ( 1 - BITTREX_FEES['taker'] )) - BITBAY_FEES['transfer'][data['currencyToBuy']]) * ( 1 - BITBAY_FEES['taker'])
    trexBayProfit = trexBayAmmount * data['bitbayBidPrice'] - trexBayBuyCost

    bayTrexAmmount = min(data['bittrexBidAmmount'], data['bitbayAskAmmount'])
    bayTrexBuyCost = bayTrexAmmount * data['bitbayAskPrice']
    bayTrexAmmount = ((bayTrexAmmount * ( 1 - BITBAY_FEES['taker'] )) - BITTREX_FEES['transfer'][data['currencyToBuy']]) * ( 1 - BITTREX_FEES['taker'])
    bayTrexProfit = bayTrexAmmount * data['bittrexBidPrice'] - bayTrexBuyCost

    if(bayTrexProfit < trexBayProfit):
        return [trexBayBuyCost, trexBayProfit, (trexBayProfit/trexBayBuyCost)*100, data['currency']]
    else: return [bayTrexBuyCost, bayTrexProfit, (bayTrexProfit/bayTrexBuyCost)*100, data['currency']]

def printProfit(data):
    print('Measures submitted to arbitration = ' + str(data[0]) + ' ' + data[3])
    print('Profit = ' + str(data[1]) + ' ' + data[3])
    print('Percent profit = ' + str(data[2]) + '%')
    print()


def main():
    while 1 > 0:
        data = downloadData(CURRENCIES['bitcoin'], CURRENCIES['dolar'])
        printPriceDifference(data)
        printProfit(calculateProfit(data))

        time.sleep(printDelay)


if __name__ == '__main__':
    main()