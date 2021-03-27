import requests
from datetime import datetime
import time
import json

API_BASE_URL = "https://api.bitbay.net/rest/trading/"


def _getApiResponse(path):
    url = API_BASE_URL + path
    headers = {'content-type': 'application/json'}

    try:
        response = requests.get(url, headers=headers).json()
        if response['status'] == 'Ok':
            return response
    except requests.exceptions.RequestException:
        print("Error while connecting to API.")
    except json.decoder.JSONDecodeError:
        print("Incorrect api response format")
    return None


def _showLastTransactions(good, currency="USD", limit=50):
    transactions = _getApiResponse(f"transactions/{good}-{currency}?limit={str(limit)}")

    if transactions:
        if transactions['items']:
            print("\n", f"Last {str(limit)} transactions for {good} in {currency}:")
            for tran in transactions['items']:
                value = float(tran['a']) * float(tran['r'])
                print("Date: ", datetime.fromtimestamp(int(float(tran['t']) / 1000)), " -  Type: ", tran['ty'],
                      " -  Value: ", value, " -  Price: ", tran['r'])
        else:
            print(f"Incorrect value of good: {good} or currency: {currency}")


def showTransactions(goods, count):
    for good in goods:
        _showLastTransactions(good[0], good[1], count)


def _mean(arr):
    return sum(arr) / len(arr)


def _sellBuyTransactionRate(transactions):
    sellPrices, buyPrices = [], []

    for tran in transactions['items']:
        if tran['ty'] == 'Sell':
            sellPrices.append(float(tran['r']))
        else:
            buyPrices.append(float(tran['r']))
    if not sellPrices or not buyPrices:
        return 'Cannot determine rate'

    meanBuyPrice, meanSellPrice = _mean(buyPrices), _mean(sellPrices)

    rate = 1 - (meanBuyPrice - meanSellPrice) / meanSellPrice
    return rate * 100


def _minSellMaxBuyRate(data: object):
    minSell = float(data['sell'][0]['ra'])
    maxBuy = float(data['buy'][9]['ra'])
    return 1 - (minSell - maxBuy) / maxBuy


def _processRateStream(goods, pathPrefix, pathSuffix, interval, source, rateFunction):
    while True:
        print("\n", datetime.now().strftime("%H:%M:%S"), f"Sell compared to buy based on {source} in percents: ")
        for good in goods:
            data = _getApiResponse(pathPrefix + good[0] + "-" + good[1] + pathSuffix)
            if data:
                print(good[0], ": Rate = ", rateFunction(data))
        time.sleep(interval)


# fromTransactions - gives rate based on last performed transactions,
# else - gives rate based on the highest buy and lowest sell price
def showPriceDifferenceStream(goods, interval=5, fromTransactions=True):
    if fromTransactions:
        _processRateStream(goods, "transactions/", "?limit=50", interval, "transactions", _sellBuyTransactionRate)
    else:
        _processRateStream(goods, "orderbook-limited/", "/10", interval, "orders", _minSellMaxBuyRate)
