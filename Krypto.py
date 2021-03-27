import requests
import time

API = "https://api.bittrex.com/api/v1.1/public/getticker?market="
currencies = ['USD-BTC', 'USD-ETH', 'USD-LTC']
printDelay = 5


def downloadData(currency):
    try:
        infoPack = requests.get(API + currency).json()
        return [currency, infoPack['result']['Bid'], infoPack['result']['Ask']]
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to API + " + infoPack.reason)
        return None


def table():
    allData = []
    for curr in currencies:
        currencyData = downloadData(curr)
        if currencyData is not None:
            allData.append(currencyData)
        else:
            print("Error, can not load " + curr + " data")
    return allData


def calculateSpread(info):
    return ((info[1] - info[2]) / info[2]) * -100


def main():
    while 1 > 0:
        for i in table():
            for j in i:
                print(str(j) + " ")
            print("Spread = " + str(round(calculateSpread(i), 3)) + "%")
            print()
        time.sleep(printDelay)


if __name__ == '__main__':
    main()
