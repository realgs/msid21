import requests
from datetime import datetime
import time
import json


# returns array of last <limit> transactions for <good> in <currency> from bitbay.net public api
def _getApiResponse(good, currency, limit=50):
    url = "https://bitbay.net/API/Public/" + good + currency + "/trades.json?sort=desc&limit=" + str(limit)
    headers = {'content-type': 'application/json'}

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Error while connecting to API.")
    except json.decoder.JSONDecodeError:
        print("Incorrect api response format. Please check url:", url)
    return []


def _getLastTransactions(good, currency="USD", limit=50):
    transactions = _getApiResponse(good, currency, limit)

    if transactions:
        print("\n", "Last " + str(limit) + " transactions for " + good + " in " + currency + ":")
        for tran in transactions:
            print("Tid: ", tran['tid'], " -  Type: ", tran['type'], " -  Price: ", tran['price'], " -  Amount: ",
                  tran['amount'], " -  Date: ", datetime.fromtimestamp(tran['date']))


def showTransactionsForCurrencies(goods, count):
    for good in goods:
        _getLastTransactions(good[0], good[1], count)


def _mean(arr):
    return sum(arr) / len(arr)


def _sellBuyPercentageRate(transactions):
    sellPrices = []
    buyPrices = []

    for tran in transactions:
        if tran['type'] == 'sell':
            sellPrices.append(tran['price'])
        else:
            buyPrices.append(tran['price'])
    if not sellPrices or not buyPrices:
        return 'Cannot determine rate'

    meanBuyPrice = _mean(buyPrices)
    meanSellPrice = _mean(sellPrices)

    rate = 1 - (meanBuyPrice - meanSellPrice) / meanSellPrice
    return rate * 100


def showPriceDifferenceStream(goods, interval=5):
    while True:
        print("\n", datetime.now().strftime("%H:%M:%S"), "Sell price compared to buy price in percents: ")
        for good in goods:
            transactions = _getApiResponse(good[0], good[1])
            if transactions:
                print(good[0], ": Rate = ", _sellBuyPercentageRate(transactions))
        time.sleep(interval)
