import requests
from datetime import datetime
import time
import json


def _getApiResponse(path):
    url = "https://api.bitbay.net/rest/trading/" + path
    headers = {'content-type': 'application/json'}

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Error while connecting to API.")
    except json.decoder.JSONDecodeError:
        print("Incorrect api response format. Please check url:", url)
    return None


def _showLastTransactions(good, currency="USD", limit=50):
    transactions = _getApiResponse("transactions/" + good + "-" + currency + "?limit=" + str(limit))

    if transactions:
        print("\n", "Last " + str(limit) + " transactions for " + good + " in " + currency + ":")
        for tran in transactions['items']:
            value = float(tran['a']) * float(tran['r'])
            print("Date: ", datetime.fromtimestamp(int(float(tran['t']) / 1000)), " -  Type: ", tran['ty'],
                  " -  Value: ", value, " -  Price: ", tran['r'])


def showTransactions(goods, count):
    for good in goods:
        _showLastTransactions(good[0], good[1], count)


def _mean(arr):
    return sum(arr) / len(arr)


def _sellBuyTransactionRate(transactions):
    sellPrices = []
    buyPrices = []

    for tran in transactions['items']:
        if tran['ty'] == 'Sell':
            sellPrices.append(float(tran['r']))
        else:
            buyPrices.append(float(tran['r']))
    if not sellPrices or not buyPrices:
        return 'Cannot determine rate'

    meanBuyPrice = _mean(buyPrices)
    meanSellPrice = _mean(sellPrices)

    rate = 1 - (meanBuyPrice - meanSellPrice) / meanSellPrice
    return rate * 100


def _minSellMaxBuyRate(data: object):
    minSell = float(data['sell'][0]['ra'])
    maxBuy = float(data['buy'][9]['ra'])
    return 1 - (minSell - maxBuy) / maxBuy


def _processRateStream(goods, pathPrefix, pathSuffix, interval, source, rateFunction):
    while True:
        print("\n", datetime.now().strftime("%H:%M:%S"), "Sell compared to buy based on " + source + " in percents: ")
        for good in goods:
            data = _getApiResponse(pathPrefix + good[0] + "-" + good[1] + pathSuffix)
            if data and data['status'] == 'Ok':
                print(good[0], ": Rate = ", rateFunction(data))
        time.sleep(interval)


# fromTransactions - gives rate based on last performed transactions,
# else - gives rate based on the highest buy and lowest sell price
def showPriceDifferenceStream(goods, interval=5, fromTransactions=True):
    if fromTransactions:
        _processRateStream(goods, "transactions/", "?limit=50", interval, "transactions", _sellBuyTransactionRate)
    else:
        _processRateStream(goods, "orderbook-limited/", "/10", interval, "orders", _minSellMaxBuyRate)

