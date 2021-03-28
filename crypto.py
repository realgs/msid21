import requests


def connectToCryptoApi(currency1, currency2):
    response = requests.get('https://bitbay.net/API/Public/' + currency1 + currency2 + '/orderbook.json')
    if response.status_code == 200:
        return response.json()
    else:
        return None


def printCryptoOffers(jsonResponse, crypto, currency, limit=5):
    if jsonResponse is not None:
        print(crypto + '/' + currency + ', BUY OFFERS:')
        print('[RATE, AMOUNT]')
        for buyOffer in jsonResponse['bids'][:limit]:
            print(buyOffer)
        print(crypto + '/' + currency + ', SELL OFFERS:')
        print('[RATE, AMOUNT]')
        for sellOffer in jsonResponse['asks'][:limit]:
            print(sellOffer)


def main():
    printCryptoOffers(connectToCryptoApi('BTC', 'USD'), 'BTC', 'USD')
    printCryptoOffers(connectToCryptoApi('LTC', 'USD'), 'LTC', 'USD')
    printCryptoOffers(connectToCryptoApi('DASH', 'USD'), 'DASH', 'USD')


if __name__ == '__main__':
    main()
