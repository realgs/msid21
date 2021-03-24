import requests
import time

API = "https://api.bittrex.com/api/v1.1/public/getticker?market="
currenciesToSearch = ['USD-BTC', 'USD-ETH', 'USD-DOGE']
delay = 5


def connectApi(currency):
    try:
        response = requests.get(API + currency)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f'Cannot connect to API {response.reason}')
        return None


def loadData(currencyName, jsonData):
    bid = jsonData['result']['Bid']
    ask = jsonData['result']['Ask']
    return [currencyName, bid, ask]


def downloadData():
    currencyInfo = []
    for currency in currenciesToSearch:
        jsonData = connectApi(currency)
        if jsonData is not None:
            currencyInfo.append(loadData(currency, jsonData))
        else:
            print(f'Cannot load market data for {currency}.')
    return currencyInfo


def printCalc(name, bid, ask):
    diff = 1 - ((ask - bid) / bid)
    print(name + f' Ask: {str(ask)} | Bid: {str(bid)}')
    print(name + f' diff in percentage: {str(diff)}')


def getDataAboutCurrencies():
    currencyInfo = downloadData()
    for [currency, bid, ask] in currencyInfo:
        printCalc(currency, bid, ask)
    print('//////////////////////////////////////////////////////')


def main():
    while 1:
        getDataAboutCurrencies()
        time.sleep(delay)


if __name__ == '__main__':
    main()
