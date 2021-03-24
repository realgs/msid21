import requests
import time

API = "https://api.bittrex.com/api/v1.1/public/getticker?market="
currencies_to_search = ['USD-BTC', 'USD-ETH', 'USD-DOGE']


def connectApi(currency):
    response = requests.get(API + currency)
    if response:
        return response.json()
    else:
        return None


def loadData(currency_name, json_data):
    bid = json_data['result']['Bid']
    ask = json_data['result']['Ask']
    return [currency_name, bid, ask]


def downloadData():
    list_of_currencies = []
    for currency in currencies_to_search:
        json_data = connectApi(currency)
        if json_data is not None:
            list_of_currencies.append(loadData(currency, json_data))
    return list_of_currencies


def printCalc(name, bid, ask):
    diff = 1 - ((ask - bid) / bid)
    print(name + ' Ask: ' + str(ask) + ' | Bid: ' + str(bid))
    print(name + ' diff in percentage: ' + str(diff))


def getDataAboutCurrencies():
    list_of_currencies = downloadData()
    for [currency, bid, ask] in list_of_currencies:
        printCalc(currency, bid, ask)
    print('//////////////////////////////////////////////////////////')


def main():
    while 1:
        getDataAboutCurrencies()
        time.sleep(5)


if __name__ == '__main__':
    main()
