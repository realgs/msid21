import json
import time
import requests

ApiUrl = "https://api.bitbay.net/rest/trading/orderbook-limited/"
headers = {'content-type': 'application/json'}
limit10 = 10
refresh = 5
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


def calculateDifference(currency):
    while True:
        data = getSellBuy(currency, limit10)
        if data is not None:
            sell = json.loads(data['sell'][0]['ra'])
            buy = json.loads(data['buy'][0]['ra'])
            result = (1 - (sell - buy) / buy) * 100
            print(f'Difference buy/sell {currency}: {result} %')
        else:
            print('There was no data to calculate the difference')
        time.sleep(refresh)


print("BTC-USD: ")
printJSON(getSellBuy(btcUsd, limit10))
print("LTC-USD:")
printJSON(getSellBuy(ltcUsd, limit10))
print("DASH-USD: ")
printJSON(getSellBuy(dashUsd, limit10))

calculateDifference(btcUsd)
# calculateDifference(ltcUsd)
# calculateDifference(dashUsd)
