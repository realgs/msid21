import requests
from threading import Timer
from enum import Enum

# Api
BITBAY_API = "https://bitbay.net/API/Public/"
BITSTAMP_API = "https://www.bitstamp.net/api/v2/"

# Enums
API = Enum('API', 'BITBAY BITSTAMP')
COMPARISON = Enum('Comparison', 'MIN MAX')

# Base variables
BASE_INTERVAL = 10
BASE_LIMIT = 3
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
    if api == API.BITBAY:
        url = f'{BITBAY_API}{cryptocurrency.upper()}{currency.upper()}/orderbook.json'
        orders = requestAPI(url)
        if orders != None:
            return {'bids': orders['bids'][:limit], 'asks': orders['asks'][:limit]}

    elif api == API.BITSTAMP:
        url = f'{BITSTAMP_API}order_book/{cryptocurrency.lower()}{currency.lower()}'
        orders = requestAPI(url)
        if orders != None:
            return {'bids': list(map(lambda el: [float(el[0]), float(el[1])], orders['bids'][:limit])), 'asks': list(map(lambda el: [float(el[0]), float(el[1])], orders['asks'][:limit]))}

    return None


def getBestOrder(orders, comparison=COMPARISON.MAX):
    if comparison == COMPARISON.MAX:
        if len(orders) > 0:
            return max(orders)
        return None

    elif comparison == COMPARISON.MIN:
        if len(orders) > 0:
            return min(orders)
        return None

    else:
        raise ValueError("Wrong comparison type")


def calculateDifference(order1=[1, 1], order2=[1, 1], fees=0, checkVolume=False):
    difference = order1[0] - order2[0] - fees

    if checkVolume:
        volume = min(order1[1], order2[1])
        return [difference, volume]

    return [difference]


def calculatePercentageDifference(order1=[1, 1], order2=[1, 1], fees=0):
    return (order1[0] - order2[0] - fees) / order2[0] * 100


def printDifference(profit, ticker, note):
    if note:
        print(f'Difference on {ticker}[{note}]: {profit:.3f}%')
    else:
        print(f'Difference on {ticker}: {profit:.3f}%')


def ex1a():
    print("Exercise 1a: ")
    for crypto in CRYPTOCURRENCIES:
        bitbayOrders = getOrders(API.BITBAY, crypto, BASE_CURRENCY)
        bitstampOrders = getOrders(API.BITSTAMP, crypto, BASE_CURRENCY)
        if bitbayOrders and bitstampOrders:
            difference = calculatePercentageDifference(
                getBestOrder(bitbayOrders['asks']),
                getBestOrder(bitstampOrders['asks']),
            )
            printDifference(difference, crypto, "BITBAY buy vs BITSTAMP buy")


def ex1b():
    print("Exercise 1b: ")
    for crypto in CRYPTOCURRENCIES:
        bitbayOrders = getOrders(API.BITBAY, crypto, BASE_CURRENCY)
        bitstampOrders = getOrders(API.BITSTAMP, crypto, BASE_CURRENCY)
        if bitbayOrders and bitstampOrders:
            difference = calculatePercentageDifference(
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX),
                getBestOrder(bitstampOrders['bids'], COMPARISON.MAX),
            )
            printDifference(difference, crypto, "BITBAY sell vs BITSTAMP sell")


def ex1c():
    print("Exercise 1c: ")
    for crypto in CRYPTOCURRENCIES:
        bitbayOrders = getOrders(API.BITBAY, crypto, BASE_CURRENCY)
        bitstampOrders = getOrders(API.BITSTAMP, crypto, BASE_CURRENCY)
        if bitbayOrders and bitstampOrders:
            diff1 = calculatePercentageDifference(
                getBestOrder(bitbayOrders['asks']), 
                getBestOrder(bitstampOrders['bids'], COMPARISON.MAX)
            )
            printDifference(diff1, crypto, "BITBAY buy vs BITSTAMP sell")

            diff2 = calculatePercentageDifference(
                getBestOrder(bitstampOrders['asks']),
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX)
            )
            printDifference(diff2, crypto, "BITSTAMP buy vs BITBAY sell")


def main():
    setInterval(ex1a, BASE_INTERVAL)
    setInterval(ex1b, BASE_INTERVAL)
    setInterval(ex1c, BASE_INTERVAL)


if __name__ == "__main__":
    main()
