import requests
from threading import Timer
from enum import Enum

BITBAY_API = "https://bitbay.net/API/Public/"
BITSTAMP_API = "https://www.bitstamp.net/api/"

APIS = Enum('API', 'BITBAY BITSTAMP')


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


def getOrdersFromApi(api, cryptocurrency, currency, limit=10):
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


def getOrdersFromMultipleApis(apis, cryptocurrency, currency, limitPerApi=10):
    buyOrders, sellOrders = [], []
    for api in apis:
        orders = getOrdersFromApi(
            api['api'], cryptocurrency, currency, limitPerApi)
        if orders != None:
            if api['asks'] == True:
                buyOrders += orders['asks']
            if api['bids'] == True:
                sellOrders += orders['bids']

    return {'asks': buyOrders, 'bids': sellOrders}


def calculateProfit(minimalArray, maximalArray):
    minimalValue, maximalValue = 1, 1
    if len(minimalArray) > 0:
        minimalValue = min(minimalArray)[0]
    if len(maximalArray) > 0:
        maximalValue = max(maximalArray)[0]

    profit = (minimalValue - maximalValue) / maximalValue * 100
    return profit


def ex1a(tickers):
    for ticker in tickers:
        orders = getOrdersFromMultipleApis(
            [{'api': APIS.BITSTAMP, 'bids': True, 'asks': False}], ticker[0], ticker[1], 10)
        print(
            f'Profit on {ticker[0]}: {calculateProfit(orders["bids"], orders["bids"]):.4f}%')


def ex1b(tickers):
    for ticker in tickers:
        orders = getOrdersFromMultipleApis(
            [{'api': APIS.BITSTAMP, 'bids': False, 'asks': True}], ticker[0], ticker[1], 10)
        print(
            f'Profit on {ticker[0]}: {calculateProfit(orders["asks"], orders["asks"]):.4f}%')


def main():
    tickers = [('BTC', 'USD')]
    setInterval(lambda: ex1a(tickers), 10)
    setInterval(lambda: ex1b(tickers), 10)


if __name__ == "__main__":
    main()
