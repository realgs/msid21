import requests
from threading import Timer
from enum import Enum

# Api
BITBAY_API = "https://bitbay.net/API/Public/"
BITSTAMP_API = "https://www.bitstamp.net/api/"
APIS = Enum('API', 'BITBAY BITSTAMP')

# Base variables
BASE_INTERVAL = 10
BASE_LIMIT = 20
BASE_CURRENCY = "USD"

# Tickers
CRYPTOCURRENCIES = ["BTC", "ETH", "LTC"]


def setInterval(func, interval):
    func()

    def func_wrapper():
        setInterval(func, interval)

    Timer(interval, func_wrapper).start()


def requestAPI(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(response.reason)
        return None


def getOrders(api, cryptocurrency, currency, limit=BASE_LIMIT):
    if api == APIS.BITBAY:
        url = f'{BITBAY_API}{cryptocurrency}{currency}/orderbook.json'
        orders = requestAPI(url)
        if orders != None:
            return {'bids': orders['bids'][:limit], 'asks': orders['asks'][:limit]}

    elif api == APIS.BITSTAMP:
        url = f'{BITSTAMP_API}order_book/{cryptocurrency}{currency}'
        orders = requestAPI(url)
        if orders != None:
            return {'bids': list(map(lambda el: [float(el[0]), float(el[1])], orders['bids'][:limit])), 'asks': list(map(lambda el: [float(el[0]), float(el[1])], orders['asks'][:limit]))}

    return None


def calculateProfit(minimalArray, maximalArray):
    minimalValue, maximalValue = 1, 1
    if len(minimalArray) > 0:
        minimalValue = min(minimalArray)[0]
    if len(maximalArray) > 0:
        maximalValue = max(maximalArray)[0]

    profit = (minimalValue - maximalValue) / maximalValue * 100
    return profit


def printProfit(profit, ticker):
    print(f'Profit on {ticker}: {profit:.4f}%')


def ex1a():
    for crypto in CRYPTOCURRENCIES:
        pass
        # TODO: Implement loop logic


def ex1b():
    for crypto in CRYPTOCURRENCIES:
        pass
        # TODO: Implement loop logic


def main():
    setInterval(ex1a, BASE_INTERVAL)
    setInterval(ex1b, BASE_INTERVAL)


if __name__ == "__main__":
    main()
