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


def calculateDifference(order1=[1, 1], order2=[1, 1], fees=0):
    difference = order1[0] - order2[0] - fees
    volume = min(order1[1], order2[1])
    return [difference, volume]



def calculatePercentageDifference(order1=[1, 1], order2=[1, 1], fees=0):
    return (order1[0] - order2[0] - fees) / order2[0] * 100


def printPercentageDifference(profit, ticker, note):
    if note:
        print(f'Difference on {ticker}[{note}]: {profit:.2f}%')
    else:
        print(f'Difference on {ticker}: {profit:.2f}%')


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
            printPercentageDifference(difference, crypto, "BITBAY:b vs BITSTAMP:b") # :b = buy, :s = sell


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
            printPercentageDifference(difference, crypto, "BITBAY:s vs BITSTAMP:s") # :b = buy, :s = sell


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
            printPercentageDifference(diff1, crypto, "BITBAY:b vs BITSTAMP:s") # :b = buy, :s = sell

            diff2 = calculatePercentageDifference(
                getBestOrder(bitstampOrders['asks']),
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX)
            )
            printPercentageDifference(diff2, crypto, "BITSTAMP:b vs BITBAY:s") # :b = buy, :s = sell

def ex2():
    print("Exercise 2: ")
    for crypto in CRYPTOCURRENCIES:
        bitbayOrders = getOrders(API.BITBAY, crypto, BASE_CURRENCY)
        bitstampOrders = getOrders(API.BITSTAMP, crypto, BASE_CURRENCY)
        if bitbayOrders and bitstampOrders:
            diff1 = calculateDifference(
                getBestOrder(bitbayOrders['asks']), 
                getBestOrder(bitstampOrders['bids'], COMPARISON.MAX)
            )
            diff1Percentage = calculatePercentageDifference(
                getBestOrder(bitbayOrders['asks']), 
                getBestOrder(bitstampOrders['bids'], COMPARISON.MAX)
            )
            printPercentageDifference(diff1Percentage, crypto, f"BITBAY:b vs BITSTAMP:s, volume: {diff1[1]:.6f}, profit: {diff1[0] * diff1[1]:.2f}{BASE_CURRENCY}") # :b = buy, :s = sell

            diff2 = calculateDifference(
                getBestOrder(bitstampOrders['asks']),
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX)
            )
            diff2Percentage = calculatePercentageDifference(
                getBestOrder(bitstampOrders['asks']),
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX)
            )
            printPercentageDifference(diff2Percentage, crypto, f"BITSTAMP:b vs BITBAY:s, volume: {diff2[1]:.6f}, profit: {diff2[0] * diff2[1]:.2f}{BASE_CURRENCY}") # :b = buy, :s = sell

def main():
    # setInterval(ex1a, BASE_INTERVAL)
    # setInterval(ex1b, BASE_INTERVAL)
    # setInterval(ex1c, BASE_INTERVAL)
    setInterval(ex2, BASE_INTERVAL)

if __name__ == "__main__":
    main()
