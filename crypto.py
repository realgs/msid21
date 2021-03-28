import requests


def connectToCryptoApi(currency1, currency2):
    response = requests.get('https://bitbay.net/API/Public/' + currency1 + currency2 + '/orderbook.json')
    if response.status_code == 200:
        return response.json()
    else:
        return None


def printCryptoOffers(jsonResponse, crypto, currency):
    if jsonResponse is not None:
        print(crypto + '/' + currency + ', BUY OFFERS:')
        print('[RATE, AMOUNT]')
        for offer in jsonResponse['bids']:
            print(offer)
        print(crypto + '/' + currency + ', SELL OFFERS:')
        print('[RATE, AMOUNT]')
        for offer in jsonResponse['asks']:
            print(offer)
        print(offer)





def main():
    printCryptoOffers(connectToCryptoApi('DASH', 'USD'), 'DASH', 'USD');


if __name__ == '__main__':
    main()
