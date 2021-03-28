import requests
import time

DELAY_OF_EXPLORING_DATA = 5
LIMIT = 5


def connectToCryptoApi(crypto, currency):
    response = requests.get('https://bitbay.net/API/Public/' + crypto + currency + '/orderbook.json')
    if response.status_code == 200:
        return response.json()
    else:
        return None


def printCryptoOffers(jsonResponse, crypto, currency, limit):
    if jsonResponse is not None:
        print(crypto + '/' + currency + ', BUY OFFERS:')
        print('[RATE, AMOUNT]')
        for buyOffer in jsonResponse['bids'][:limit]:
            print(buyOffer)
        print(crypto + '/' + currency + ', SELL OFFERS:')
        print('[RATE, AMOUNT]')
        for sellOffer in jsonResponse['asks'][:limit]:
            print(sellOffer)


def calculateDifferenceRatio(crypto, currency, limit=10):
    jsonResponse = connectToCryptoApi(crypto, currency)
    if jsonResponse is not None:
        buyOffers = jsonResponse['bids'][:limit]
        sellOffers = jsonResponse['asks'][:limit]
        buyOffersCount = len(buyOffers)
        sellOffersCount = len(sellOffers)
        offersCount = min(buyOffersCount, sellOffersCount)
        for offerIndex in range(offersCount):
            buyPrice = buyOffers[offerIndex][0]
            sellPrice = sellOffers[offerIndex][0]
            differenceRatio = 1 - (sellPrice - buyPrice) / buyPrice
            print('Difference ratio in %: ' + crypto + '/' + currency + ': ', differenceRatio)


def calcDifference(crypto, currency, delayOfExploringData):
    while True:
        calculateDifferenceRatio(crypto, currency)
        time.sleep(delayOfExploringData)


def main():
    printCryptoOffers(connectToCryptoApi('BTC', 'USD'), 'BTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('LTC', 'USD'), 'LTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('DASH', 'USD'), 'DASH', 'USD', LIMIT)

    calcDifference('BTC', 'USD', DELAY_OF_EXPLORING_DATA)
    # calcDifference('LTC', 'USD', DELAY_OF_EXPLORING_DATA)
    # calcDifference('DASH', 'USD', DELAY_OF_EXPLORING_DATA)


if __name__ == '__main__':
    main()
