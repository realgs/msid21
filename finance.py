import requests
from datetime import datetime


def _getLastTransactions(good, limit=50):
    url = "https://bitbay.net/API/Public/" + good + "/trades.json?sort=desc&limit=" + str(limit)

    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers)

    print()
    if response.status_code == 200:
        print("Last " + str(limit) + " transactions for " + good + ":")
        for tran in response.json():
            print("Tid: ", tran['tid'], " -  Type: ", tran['type'], " -  Price: ", tran['price'], " -  Amount: ",
                  tran['amount'], " -  Date: ", datetime.fromtimestamp(tran['date']))
    else:
        print(response.reason)


def showTransactionsForCurrencies(currencies, count):
    for curr in currencies:
        _getLastTransactions(curr, count)


myCurrencies = ["BTC", "ETH", "ZEC"]
showTransactionsForCurrencies(myCurrencies, 10)
