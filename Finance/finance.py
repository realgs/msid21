import json

import requests

ApiUrl = "https://api.bitbay.net/rest/trading/orderbook-limited/"
headers = {'content-type': 'application/json'}
limit10 = 10
btcUsd = "BTC-USD"
ltcUsd = "LTC-USD"
dashUsd = "DASH-USD"


def getSellBuy(currency, limit):
    url = f'{ApiUrl}{currency}/{limit}'
    response = requests.request("GET", url, headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def printJSON(obj):
    msg = json.dumps(obj, indent=4)
    print(msg)


print("BTC-USD: ")
printJSON(getSellBuy(btcUsd, limit10))
print("LTC-USD:")
printJSON(getSellBuy(ltcUsd, limit10))
print("DASH-USD: ")
printJSON(getSellBuy(dashUsd, limit10))





