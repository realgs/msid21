import requests
from time import sleep

API = "https://bitbay.net/API/Public/"
BASE_CURRENCY = "USD"
CRYPTOCURRENCIES = ["BTC", "LTC", "DASH"]
INTERVAL = 5
BASE_LIMIT = 20
FIND_AVERAGE_PROFIT = False


def setInterval(func, interval):
    func()
    sleep(5)
    setInterval(func, interval)


def requestAPI(url):
    response = requests.get(url)

    if response.status_code in range(200, 299):
        return response.json()
    else:
        print(response.reason)
        return None


def getOrders(cryptocurrency, currency, limit=BASE_LIMIT):
    url = f'{API}{cryptocurrency}{currency}/orderbook.json'
    orders = requestAPI(url)
    if orders != None:
        return {'bids': orders['bids'][:limit], 'asks': orders['asks'][:limit]}
    return None


def printOrders(orders, cryptocurrency, currency):
    if orders != None:
        sellOrders = orders['bids']
        buyOrders = orders['asks']

        print(f'{cryptocurrency}:{currency} | BUY ORDERS:')
        for order in buyOrders:
            printOrder(cryptocurrency, currency, order)

        print(f'{cryptocurrency}:{currency} | SELL ORDERS:')
        for order in sellOrders:
            printOrder(cryptocurrency, currency, order)


def printOrder(cryptocurrency, currency, order):
    print(f'{order[1]} {cryptocurrency} for {(order[0] * order[1]):.2f} {currency}')


def findProfit(orders, cryptocurrency, currency, average=False):
    if orders != None:
        sellOrders, buyOrders = orders['bids'], orders['asks']
        buyPrice, sellPrice = 0, 0
        if average:
            sumOfBuyPrice = 0
            sumOfSellPrice = 0
            length = min(len(buyOrders), len(sellOrders))

            for index in range(length):
                sumOfBuyPrice = sumOfBuyPrice + (buyOrders[index][0])
                sumOfSellPrice = sumOfSellPrice + (sellOrders[index][0])

            buyPrice = sumOfBuyPrice / length
            sellPrice = sumOfSellPrice / length
        else:
            buyPrice = max(buyOrders)[0]
            sellPrice = min(sellOrders)[0]

        return calculateProfit(sellPrice, buyPrice)

    return 0

def calculateProfit(sellPrice=1, buyPrice=1):
    return 1 - (sellPrice - buyPrice) / buyPrice


def printProfit(profit, cryptocurrency, average=False):
    if average:
        print(f'Average profit on: {cryptocurrency} = {profit:.2f}%')
    else:
        print(f'Profit on: {cryptocurrency} = {profit:.2f}%')

def ex1():
    for crypto in CRYPTOCURRENCIES:
        orders = getOrders(crypto, BASE_CURRENCY, 3)
        printOrders(orders, crypto, BASE_CURRENCY)


def ex2():
    for crypto in CRYPTOCURRENCIES:
        orders = getOrders(crypto, BASE_CURRENCY)
        profit = findProfit(orders, crypto, BASE_CURRENCY, FIND_AVERAGE_PROFIT)
        printProfit(profit, crypto, FIND_AVERAGE_PROFIT)


def main():
    print("Exercise 1:")
    ex1()
    print("Exercise 2:")
    setInterval(ex2, INTERVAL)


if __name__ == "__main__":
    main()
