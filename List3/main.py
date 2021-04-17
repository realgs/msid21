from threading import Thread

import requests
import time

# api data
BITBAY = {
    "name": "BITBAY",
    "url": 'https://bitbay.net/API/Public/{}/{}.json',
    "asks_prompt": 'asks',
    "bids_prompt": 'bids',
    "rate_prompt": 0,
    "quantity_prompt": 1,
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
    "asks_prompt": 'ask',
    "bids_prompt": 'bid',
    "rate_prompt": 'rate',
    "quantity_prompt": 'quantity',
    "taker": 0.0035,
    "transfer": {
        'BTC': 0.0003,
        'ETH': 0.006,
        'LTC': 0.01
    }
}

# general data
CURRENCIES = ['BTC', 'ETH', 'LTC']
ORDERBOOK = 'orderbook'
BASE_CURRENCY = 'USD'
DELAY = 5


def getOffers(currency, api):
    offerList = requests.get(api['url'].format(currency, ORDERBOOK))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def printOffers(api):
    name = api['name']
    print(f"\nOffers for {name}:\n")
    for currency in CURRENCIES:
        print(f'{currency}-{BASE_CURRENCY}')
        print("\tbids: ", end='')
        print(getOffers(f'{currency}-{BASE_CURRENCY}', api)[api['bids_prompt']])
        print("\tasks: ", end='')
        print(getOffers(f'{currency}-{BASE_CURRENCY}', api)[api['asks_prompt']])


def downloadData(currency, api):
    offersData = getOffers(currency, api)
    if offersData:
        bids = offersData[api['bids_prompt']]
        asks = offersData[api['asks_prompt']]
        return [bids, asks]
    else:
        print(f'Cannot load market data for {currency} from {api}!')
        return None


def calculateDifference(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def findDifferenceBid(currency, api1, api2):
    bid_api1 = getBestBid(currency, api1)
    bid_api2 = getBestBid(currency, api2)
    print(f'Best bid: {api1["name"]}: {bid_api1}\t\t-\t\t{api2["name"]}: {bid_api2}')
    return calculateDifference(float(bid_api2), float(bid_api1))


# zad 1b
def printDifferenceBid(api1, api2):
    print("Bids:")
    for currency in CURRENCIES:
        difference = findDifferenceBid(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


def findDifferenceAsk(currency, api1, api2):
    bid_api1 = getBestAsk(currency, api1)
    bid_api2 = getBestAsk(currency, api2)
    print(f'Best ask: {api1["name"]}: {bid_api1}\t\t-\t\t{api2["name"]}: {bid_api2}')
    return calculateDifference(float(bid_api2), float(bid_api1))


# zad 1a
def printDifferenceAsk(api1, api2):
    print("Asks:")
    for currency in CURRENCIES:
        difference = findDifferenceAsk(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


def getBestBid(currency, api):
    [bids, asks] = downloadData(currency, api)
    return [bids, asks][0][0][api['rate_prompt']]


def getBestAsk(currency, api):
    [bids, asks] = downloadData(currency, api)
    return [bids, asks][1][0][api['rate_prompt']]


def calculateDifferenceBetweenApis(currency, api1, api2):
    bid_api1 = getBestBid(currency, api1)
    ask_api2 = getBestAsk(currency, api2)
    print(f'Best offers: \t\t\tbid: {api1["name"]} {bid_api1}\t\t\t\t\task: {api2["name"]} {ask_api2}')
    return calculateDifference(float(ask_api2), float(bid_api1))


# zad 1c
def printDifferenceApis(api1, api2):
    print("Apis:")
    for currency in CURRENCIES:
        difference = calculateDifferenceBetweenApis(f'{currency}-{BASE_CURRENCY}', api1, api2)
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


# zad 2
def isArbitragePossible(bid_rate, ask_rate):
    return float(bid_rate) > float(ask_rate)


def countTakerAddTransferFee(offer, api, currency):
    return offer * api['taker'] + offer * api['transfer'][currency]


def countTakerFee(offer, api):
    return offer * api['taker']


def calculateArbitrage(currency, api1, api2):
    [bids_api1, _] = downloadData(currency, api1)
    [_, asks_api2] = downloadData(currency, api2)

    if isArbitragePossible(getBestBid(currency, api1), getBestAsk(currency, api2)):
        i, j, askQuantity, bidQuantity, askValue, bidValue, asksFee, bidsFee = 0, 0, 0, 0, 0, 0, 0, 0
        for ask in asks_api2:
            if float(ask['rate_prompt']) < float(bids_api1[0]['rate_prompt']):
                askQuantity = float(ask['quantity_prompt'])
                i += 1
        for bid in bids_api1:
            if float(bid['rate_prompt']) < float(asks_api2[i-1]['rate_prompt']):
                bidQuantity = float(bid['quantity_prompt'])
                j += 1

        while askQuantity < bidQuantity:
            # zabierz bid  z końca
            bidQuantity -= float(bids_api1[j-1]['quantity_prompt'])
            j -= 1
        leftoverQuantity = askQuantity - bidQuantity
        leftoverValue = 0
        if j == 0:
            print(f"Arbitrage for {currency} impossible!")
            print(f'Buying from {api2["name"]} and selling to {api1["name"]}')
        else:
            while i > 0:
                askValue += float(asks_api2[i-1]['rate_prompt']) * float(asks_api2[i-1]['quantity_prompt'])
                asksFee += countTakerAddTransferFee(asks_api2[i-1]['rate_prompt'], api2, currency)
                if leftoverQuantity < float(asks_api2[i-1]['quantity_prompt']):
                    leftoverValue += leftoverQuantity * float(asks_api2[i-1]['rate_prompt'])
                    leftoverQuantity = 0
                else:
                    leftoverValue += float(asks_api2[i - 1]['quantity_prompt']) * float(asks_api2[i - 1]['rate_prompt'])
                    leftoverQuantity -= float(asks_api2[i - 1]['quantity_prompt'])
                i -= 1
            while j > 0:
                bidValue += float(bids_api1[j-1]['rate_prompt']) * float(bids_api1[j-1]['quantity_prompt'])
                bidsFee += countTakerFee(bids_api1[j-1]['rate_prompt'], api1)
                j -= 1

        sumFees = asksFee + bidsFee
        baseProfit = bidValue - (askValue - leftoverValue)
        totalProfit = baseProfit - sumFees
        print("Arbitrage was possible!")
        print(f'Buying from {api2["name"]} and selling to {api1["name"]}')
        print(f'Total profit for {currency}:\t{totalProfit}')

    else:
        print(f"Arbitrage for {currency} impossible!")
        print(f'Buying from {api2["name"]} and selling to {api1["name"]}')


def main():
    while True:
        printOffers(BITBAY)
        printOffers(BITTREX)

        printDifferenceBid(BITTREX, BITBAY)
        printDifferenceAsk(BITBAY, BITTREX)

        printDifferenceApis(BITBAY, BITTREX)
        printDifferenceApis(BITTREX, BITBAY)

        calculateArbitrage('BTC-USD', BITBAY, BITTREX)
        calculateArbitrage('LTC-USD', BITTREX, BITBAY)
        print('\n---------------------------------------------------\n')
        time.sleep(DELAY)


if __name__ == '__main__':
    main()
