import requests
import time

# api data
BITBAY = {
    "name": "BITBAY",
    "url": 'https://bitbay.net/API/Public/{}/{}.json',
    "asks": 'asks',
    "bids": 'bids',
    "rate": 0,
    "quantity": 1,
    "taker": 0.0043,
    "transfer": {
        'BTC': 0.0005,
        'ETH': 0.01,
        'LTC': 0.001
    }
}

BITTREX = {
    "name": "BITTREX",
    "url": 'https://api.bittrex.com/v3/markets/{}/{}',
    "asks": 'ask',
    "bids": 'bid',
    "rate": 'rate',
    "quantity": 'quantity',
    "taker": 0.0035,
    "transfer": {
        'BTC': 0.0005,
        'ETH': 0.006,
        'LTC': 0.01
    }
}

# general data
CURRENCIES = ['BTC', 'LTC']
ORDERBOOK = 'orderbook'
BASE_CURRENCY = 'USD'
DELAY = 5


def getOffers(currency, api):
    offerList = requests.get(api['url'].format(currency, ORDERBOOK))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def downloadData(currency, api):
    offersData = getOffers(currency, api)
    if offersData:
        bids = offersData[api['bids']]
        asks = offersData[api['asks']]
        return [bids, asks]
    else:
        print(f'Cannot load market data for {currency} from {api["name"]}!')
        return None


def calculateDifference(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def getBestBid(currency, api):
    [bids, asks] = downloadData(currency, api)
    return [bids, asks][0][0][api['rate']]


def getBestAsk(currency, api):
    [bids, asks] = downloadData(currency, api)
    return [bids, asks][1][0][api['rate']]


def findDifferenceBid(currency, api1, api2):
    bid_api1 = getBestBid(currency, api1)
    bid_api2 = getBestBid(currency, api2)
    print(f'Best bid: {api1["name"]}: {bid_api1}\t\t-\t\t{api2["name"]}: {bid_api2}')
    return calculateDifference(float(bid_api2), float(bid_api1))


def findDifferenceAsk(currency, api1, api2):
    bid_api1 = getBestAsk(currency, api1)
    bid_api2 = getBestAsk(currency, api2)
    print(f'Best ask: {api1["name"]}: {bid_api1}\t\t-\t\t{api2["name"]}: {bid_api2}')
    return calculateDifference(float(bid_api2), float(bid_api1))


def calculateDifferenceBetweenApis(currency, api1, api2):
    bid_api1 = getBestBid(currency, api1)
    ask_api2 = getBestAsk(currency, api2)
    print(f'Best offers: \t\t\tbid: {api1["name"]} {bid_api1}\t\t\t\t\task: {api2["name"]} {ask_api2}')
    return calculateDifference(float(ask_api2), float(bid_api1))


# zad 1a
def printDifferenceAsk(api1, api2):
    print("Asks:")
    for currency in CURRENCIES:
        difference = findDifferenceAsk(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


# zad 1b
def printDifferenceBid(api1, api2):
    print("Bids:")
    for currency in CURRENCIES:
        difference = findDifferenceBid(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


# zad 1c
def printDifferenceApis(api1, api2):
    print("Apis:")
    for currency in CURRENCIES:
        difference = calculateDifferenceBetweenApis(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


# zad 2
def calculateCost(quantity, rate, api, currency):
    return float(rate) * (float(quantity) + float(api['transfer'][currency] + float(quantity) * float(api['taker'])))


def calculateProfit(quantity, rate, api):
    return float(rate) * float(quantity) * (1 - float(api['taker']))


def printArbitrageImpossible(currency, api1, api2):
    print(f"Arbitrage for {currency} impossible!")
    print(f'Buying from {api2["name"]} and selling to {api1["name"]}')


def calculateArbitrage(currency, api1, api2):
    [bids_api1, _] = downloadData(f'{currency}-{BASE_CURRENCY}', api1)
    [_, asks_api2] = downloadData(f'{currency}-{BASE_CURRENCY}', api2)

    i, j, askQuantity, bidQuantity, cost, profit = 0, 0, 0, 0, 0, 0
    for ask in asks_api2:
        if float(ask[api2['rate']]) < float(bids_api1[0][api1['rate']]):
            askQuantity += float(ask[api2['quantity']])
            i += 1
    for bid in bids_api1:
        if float(bid[api1['rate']]) > float(asks_api2[i - 1][api2['rate']]):
            bidQuantity += float(bid[api1['quantity']])
            j += 1
    finalAsks = asks_api2[:i]
    finalBids = bids_api1[:j]
    while askQuantity < bidQuantity:
        finalBids.sort(key=lambda x: x[api1['quantity']])
        bidQuantity -= finalBids[0][api1['quantity']]
        finalBids = finalBids[1:]

    leftoverQuantity = askQuantity - bidQuantity
    if not finalAsks or not finalBids:
        printArbitrageImpossible(currency, api1, api2)
    else:
        for ask in finalAsks:
            cost += calculateCost(ask[api2['quantity']], ask[api2['rate']], api2, currency)
        for bid in finalBids:
            profit += calculateProfit(bid[api1['quantity']], bid[api1['rate']], api1)

        baseIncome = profit - cost
        if baseIncome < 0:
            printArbitrageImpossible(currency, api1, api2)
        else:
            print("Arbitrage was possible!")
            print(f'Buying from {api2["name"]} and selling to {api1["name"]}')
            print(f'Total profit for {currency}:\t{baseIncome}USD')
            print(f'Profit in percentage: {calculateDifference(cost, profit)}')
            print(f'Quantity of the currency: BOUGHT: {askQuantity}, SOLD: {bidQuantity}, LEFT: {leftoverQuantity}')


def main():
    while True:
        printDifferenceBid(BITTREX, BITBAY)
        printDifferenceAsk(BITBAY, BITTREX)

        printDifferenceApis(BITBAY, BITTREX)
        printDifferenceApis(BITTREX, BITBAY)

        calculateArbitrage('BTC', BITBAY, BITTREX)
        calculateArbitrage('BTC', BITTREX, BITBAY)
        print('\n---------------------------------------------------\n')
        time.sleep(DELAY)


if __name__ == '__main__':
    main()
