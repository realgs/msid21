import requests
import time

DELAY_OF_EXPLORING_DATA = 5
LIMIT = 5
RATE_AMOUNT_TEXT = '[RATE, AMOUNT]'


def connectToCryptoApi(crypto, currency):
    response = requests.get('https://bitbay.net/API/Public/' + crypto + currency + '/orderbook.json')
    if response.status_code in (200, 299):
        return response.json()
    else:
        return None


def printCryptoOffers(jsonResponse, crypto, currency, limit):
    if jsonResponse is not None:
        print(crypto + '/' + currency + ', BUY OFFERS:')
        print(RATE_AMOUNT_TEXT)
        for buyOffer in jsonResponse['bids'][:limit]:
            print(buyOffer)
        print(crypto + '/' + currency + ', SELL OFFERS:')
        print(RATE_AMOUNT_TEXT)
        for sellOffer in jsonResponse['asks'][:limit]:
            print(sellOffer)


def calculateDifferenceRatio(crypto, currency):
    jsonResponse = connectToCryptoApi(crypto, currency)
    if jsonResponse is not None:
        buyOffers = jsonResponse['bids']
        sellOffers = jsonResponse['asks']
        buyPrice = buyOffers[0][0]
        sellPrice = sellOffers[0][0]
        differenceRatio = 1 - (sellPrice - buyPrice) / buyPrice
    return differenceRatio


def printCalcDifference(crypto, currency, delayOfExploringData):
    while True:
        print('Difference ratio in %: ' + crypto + '/' + currency + ': ', calculateDifferenceRatio(crypto, currency))
        time.sleep(delayOfExploringData)


def main():
    printCryptoOffers(connectToCryptoApi('BTC', 'USD'), 'BTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('LTC', 'USD'), 'LTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('DASH', 'USD'), 'DASH', 'USD', LIMIT)

    # printCalcDifference('BTC', 'USD', DELAY_OF_EXPLORING_DATA)
    printCalcDifference('LTC', 'USD', DELAY_OF_EXPLORING_DATA)
    # printCalcDifference('DASH', 'USD', DELAY_OF_EXPLORING_DATA)


if __name__ == '__main__':
    main()
