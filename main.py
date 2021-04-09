import requests
from threading import Timer
from enum import Enum

# Api
BITBAY_API = "https://bitbay.net/API/Public/"
BITSTAMP_API = "https://www.bitstamp.net/api/v2/"

# Fees
BITBAY_FEE = {
    'transaction': 0.001,  # of the trade
    'withdrawal': {  # static value
        'BTC': 0.0005,
        'ETH': 0.01,
        'LTC': 0.001
    }
}
BITSTAMP_FEE = {
    'transaction': 0.0025,  # of the trade
    'withdrawal': {  # static value
        'BTC': 0.0005,
        'ETH': 0.03,
        'LTC': 0.001
    }
}

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


def getBestOrder(orders, comparison=COMPARISON.MIN):
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


def calculateFees(transactionApi, withdrawalApi, cryptocurrency, quantity):
    fee = 0

    # Transaction fee
    if transactionApi == API.BITBAY:
        fee += quantity * BITBAY_FEE['transaction']

    elif transactionApi == API.BITSTAMP:
        fee += quantity * BITSTAMP_FEE['transaction']

    # Withdrawal fee
    if withdrawalApi == API.BITBAY:
        if(BITBAY_FEE['withdrawal'][cryptocurrency]):
            fee += BITBAY_FEE['withdrawal'][cryptocurrency]

    elif withdrawalApi == API.BITSTAMP:
        if(BITBAY_FEE['withdrawal'][cryptocurrency]):
            fee += BITBAY_FEE['withdrawal'][cryptocurrency]

    return fee  # Returns value in cryptocurency ex. 0,00015 BTC


def calculateDifference(order1=[1, 1], order2=[1, 1], fees=0):
    difference = order1[0] - order2[0]
    volume = min(order1[1], order2[1]) - fees
    return [difference, volume]


def calculatePercentageDifference(order1=[1, 1], order2=[1, 1]):
    return (order1[0] - order2[0]) / order2[0] * 100


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
                getBestOrder(bitbayOrders['bids'], COMPARISON.MAX),
                getBestOrder(bitstampOrders['bids'], COMPARISON.MAX),
            )
            printPercentageDifference(
                difference, crypto, "BITBAY:b vs BITSTAMP:b")  # :b = buy, :s = sell


def ex1b():
    print("Exercise 1b: ")
    for crypto in CRYPTOCURRENCIES:
        bitbayOrders = getOrders(API.BITBAY, crypto, BASE_CURRENCY)
        bitstampOrders = getOrders(API.BITSTAMP, crypto, BASE_CURRENCY)
        if bitbayOrders and bitstampOrders:
            difference = calculatePercentageDifference(
                getBestOrder(bitbayOrders['asks']),
                getBestOrder(bitstampOrders['asks']),
            )
            printPercentageDifference(
                difference, crypto, "BITBAY:s vs BITSTAMP:s")  # :b = buy, :s = sell


def ex1c():
    trades = [
        [API.BITSTAMP, API.BITBAY],
        [API.BITBAY, API.BITSTAMP]
    ]  # [[from, to]]
    orders = {}  # dictionary with already fetched orders

    print("Exercise 1c: ")
    for crypto in CRYPTOCURRENCIES:
        for trade in trades:
            # Checking if orders have already been fetched
            if trade[0] not in orders:
                orders[trade[0]] = getOrders(trade[0], crypto, BASE_CURRENCY)
            if trade[1] not in orders:
                orders[trade[1]] = getOrders(trade[1], crypto, BASE_CURRENCY)

            # Calculating difference (profit)
            if trade[0] in orders and trade[1] in orders:
                diff = calculatePercentageDifference(
                    getBestOrder(orders[trade[0]]['bids']),
                    getBestOrder(orders[trade[1]]['asks'], COMPARISON.MAX)
                )
                printPercentageDifference(
                    diff,
                    crypto,
                    f"{trade[0].name}:b vs {trade[1].name}:s"
                )  # :b = buy, :s = sell


def ex2():
    trades = [
        [API.BITSTAMP, API.BITBAY],
        [API.BITBAY, API.BITSTAMP]
    ]  # [[from, to]]
    orders = {}  # dictionary with already fetched orders

    print("Exercise 2: ")
    for crypto in CRYPTOCURRENCIES:
        for trade in trades:
            # Checking if orders have already been fetched
            if trade[0] not in orders:
                orders[trade[0]] = getOrders(trade[0], crypto, BASE_CURRENCY)
            if trade[1] not in orders:
                orders[trade[1]] = getOrders(trade[1], crypto, BASE_CURRENCY)

            # Calculating difference (profit)
            if trade[0] in orders and trade[1] in orders:
                bestBuyOrder = getBestOrder(orders[trade[0]]['bids'])
                bestSellOrder = getBestOrder(
                    orders[trade[1]]['asks'], COMPARISON.MAX)
                fees = calculateFees(trade[0], trade[1], crypto, min(
                    bestBuyOrder[1], bestSellOrder[1]))

                diff = calculateDifference(
                    bestBuyOrder,
                    bestSellOrder,
                    fees
                )
                diffPercentage = calculatePercentageDifference(
                    bestBuyOrder,
                    bestSellOrder
                )

                printPercentageDifference(
                    diffPercentage,
                    crypto,
                    f"{trade[0].name}:b -> {trade[1].name}:s, volume: {diff[1]:.6f}, profit: {diff[0] * diff[1]:.2f}{BASE_CURRENCY}"
                )  # :b = buy, :s = sell


def main():
    setInterval(ex1a, BASE_INTERVAL)
    setInterval(ex1b, BASE_INTERVAL)
    setInterval(ex1c, BASE_INTERVAL)
    setInterval(ex2, BASE_INTERVAL)


if __name__ == "__main__":
    main()
