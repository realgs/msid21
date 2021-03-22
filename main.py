import requests

API = "https://bitbay.net/API/Public/"


def requestAPI(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(response.reason)
        return None


def getOrders(cryptocurrency, currency, limit=10):
    url = f'{API}{cryptocurrency}{currency}/orderbook.json'
    orders = requestAPI(url)
    if orders != None:
        return {'bids': orders['bids'][:limit], 'asks': orders['asks'][:limit]}
    return None


def printOrders(cryptocurrency, currency, limit = 4):
    orders = getOrders(cryptocurrency, currency, limit)
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
    print(f'{order[1]} {cryptocurrency} for {order[0] } {currency}')


def calculateProfit(cryptocurrency, currency, limit=5):
    orders = getOrders(cryptocurrency, currency, limit)
    if orders != None:
        sellOrders = orders['bids']
        buyOrders = orders['asks']
        sumOfBuyPrice = 0
        sumOfSellPrice = 0
        length = min(len(buyOrders), len(sellOrders))

        for index in range(length):
            sumOfBuyPrice = sumOfBuyPrice + (buyOrders[index][0])
            sumOfSellPrice = sumOfSellPrice + (sellOrders[index][0])

        averageBuyPrice = sumOfBuyPrice/length
        averageSellPrice = sumOfSellPrice/length
        profit = 1 - (averageSellPrice - averageBuyPrice) / averageBuyPrice * 100
        print(f'Average profit on: {cryptocurrency} = {profit:.3}%')


def ex1():
    printOrders('BTC', 'USD')
    printOrders('LTC', 'USD')
    printOrders('DASH', 'USD')


def ex2():
    calculateProfit('BTC', 'USD')
    calculateProfit('LTC', 'USD')
    calculateProfit('DASH', 'USD')


def main():
    print("Exercise 1:")
    ex1()
    print("Exercise 2:")
    ex2()


if __name__ == "__main__":
    main()
