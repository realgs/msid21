import requests
from datetime import datetime


def _getApiResponse(good, limit=50):
    url = "https://bitbay.net/API/Public/" + good + "/trades.json?sort=desc&limit=" + str(limit)

    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.reason)
        return []


def _getLastTransactions(good, limit=50):
    transactions = _getApiResponse(good, limit)
    if transactions:
        print("\n", "Last " + str(limit) + " transactions for " + good + ":")
        for tran in transactions:
            print("Tid: ", tran['tid'], " -  Type: ", tran['type'], " -  Price: ", tran['price'], " -  Amount: ",
                  tran['amount'], " -  Date: ", datetime.fromtimestamp(tran['date']))


def showTransactionsForCurrencies(currencies, count):
    for curr in currencies:
        _getLastTransactions(curr, count)


def calculateMean(arr):
    return sum(arr) / len(arr)


def showPriceDifferenceStream(good):
    transactions = _getApiResponse(good)
    if transactions:
        sellPrices = []
        buyPrices = []
        for tran in transactions:
            if tran['type'] == 'sell':
                sellPrices.append(tran['price'])
            else:
                buyPrices.append(tran['price'])
        meanBuyPrice = calculateMean(buyPrices)
        meanSellPrice = calculateMean(sellPrices)
        diff = 1 - (meanBuyPrice - meanSellPrice) / meanSellPrice
        print("Roznica kupno - sprzedaż = ", diff)


myCurrencies = ["BTC", "ETH", "ZEC"]
showTransactionsForCurrencies(myCurrencies, 10)

showPriceDifferenceStream("BTC")
