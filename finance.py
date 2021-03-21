import requests
from datetime import datetime
import time

# returns array of last <limit> transactions for <good> from bitbay.net public api
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


def _mean(arr):
    return sum(arr) / len(arr)


def _sellBuyDifference(transactions):
    sellPrices = []
    buyPrices = []
    for tran in transactions:
        if tran['type'] == 'sell':
            sellPrices.append(tran['price'])
        else:
            buyPrices.append(tran['price'])
    meanBuyPrice = _mean(buyPrices)
    meanSellPrice = _mean(sellPrices)
    return 1 - (meanBuyPrice - meanSellPrice) / meanSellPrice


def showPriceDifferenceStream(currencies, interval=5):
    while True:
        print("\n", datetime.now().strftime("%H:%M:%S"), "Cena sprzedazy wzgledem ceny kupna w procentach: ")
        for currency in currencies:
            transactions = _getApiResponse(currency)
            if transactions:
                print(currency, ": Wskaznik = ", _sellBuyDifference(transactions))
        time.sleep(interval)
