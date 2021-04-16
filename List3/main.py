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


def findDifferenceBid(currency):
    bid_BITBAY = getBestBid(currency, BITBAY)
    bid_BITTREX = getBestBid(currency, BITTREX)
    print(f'Best bid: BITBAY: {bid_BITBAY}\t\t-\t\tBITTREX: {bid_BITTREX}')
    return calculateDifference(float(bid_BITTREX), float(bid_BITBAY))


# zad 1b
def printDifferenceBid():
    print("Bids:")
    for currency in CURRENCIES:
        difference = findDifferenceBid(f'{currency}-{BASE_CURRENCY}')
        print(f'Currency: {currency}-{BASE_CURRENCY}\t\tDifference: {difference}%')


def findDifferenceAsk(currency):
    bid_BITBAY = getBestAsk(currency, BITBAY)
    bid_BITTREX = getBestAsk(currency, BITTREX)
    print(f'Best ask: BITBAY: {bid_BITBAY}\t\t-\t\tBITTREX: {bid_BITTREX}')
    return calculateDifference(float(bid_BITTREX), float(bid_BITBAY))


# zad 1a
def printDifferenceAsk():
    print("Asks:")
    for currency in CURRENCIES:
        difference = findDifferenceAsk(f'{currency}-{BASE_CURRENCY}')
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


def main():
    # printOffers(BITBAY)
    # printOffers(BITTREX)

    # printDifferenceBid()
    # printDifferenceAsk()

    printDifferenceApis(BITBAY, BITTREX)
    printDifferenceApis(BITTREX, BITBAY)

    # print_currency_offers(BITTREX)
    # print_currency_offers(BITBAY)


if __name__ == '__main__':
    main()
