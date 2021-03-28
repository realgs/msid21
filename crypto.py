import requests
import time

DELAY_OF_EXPLORING_DATA = 20
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


def calculateProfit(crypto, currency, limit):
    jsonResponse = connectToCryptoApi(crypto, currency)
    sumOfBuyPrice = 0
    sumOfSellPrice = 0
    if jsonResponse is not None:
        for buyOffer in jsonResponse['bids'][:limit]:
            sumOfBuyPrice = sumOfBuyPrice + buyOffer[0]
        for sellOffer in jsonResponse['asks'][:limit]:
            sumOfSellPrice = sumOfSellPrice + sellOffer[0]
    averageOfBuyPrice = sumOfBuyPrice / limit
    averageOfSellPrice = sumOfSellPrice / limit
    profit = (1 - (averageOfSellPrice - averageOfBuyPrice) / averageOfBuyPrice) * 100
    return profit


def showProfit(crypto, currency, delayOfExploringData, limit):
    while True:
        profit = calculateProfit(crypto, currency, limit)
        print('Profit: ' + crypto + '/' + currency + ': ', profit)
        time.sleep(delayOfExploringData)


def main():
    printCryptoOffers(connectToCryptoApi('BTC', 'USD'), 'BTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('LTC', 'USD'), 'LTC', 'USD', LIMIT)
    printCryptoOffers(connectToCryptoApi('DASH', 'USD'), 'DASH', 'USD', LIMIT)

    # showProfit('BTC', 'USD', DELAY_OF_EXPLORING_DATA, 1)
    showProfit('LTC', 'USD', DELAY_OF_EXPLORING_DATA, 1)
    # showProfit('DASH', 'USD', DELAY_OF_EXPLORING_DATA, 1)


if __name__ == '__main__':
    main()
