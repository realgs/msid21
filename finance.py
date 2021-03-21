import requests
from datetime import datetime


def getLastTransactions(good):
    url = "https://bitbay.net/API/Public/" + good + "/trades.json?sort=desc"

    response = requests.get(url)

    print()
    if response.status_code == 200:
        print("Last 50 transactions for " + good + ":")
        for tran in response.json():
            print("Tid: ", tran['tid'], " -  Type: ", tran['type'], " -  Price: ", tran['price'], " -  Amount: ",
                  tran['amount'], " -  Date: ", datetime.fromtimestamp(tran['date']))
    else:
        print(response.reason)


currencies = ["BTC", "ETH", "ZEC"]
for curr in currencies:
    getLastTransactions(curr)
