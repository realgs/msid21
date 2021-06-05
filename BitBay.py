import requests

import CurrencyChange

BITBAY_ORDER_URL_PREFIX = 'https://bitbay.net/API/Public/'
BITBAY_ORDER_URL_POSTFIX = '/orderbook.json'
BITBAY_TAKER_FEE = 0.0042

def value(resource, ammount, baseCurrency):

    bitbayDownload = requests.get(BITBAY_ORDER_URL_PREFIX + resource + 'USD' + BITBAY_ORDER_URL_POSTFIX)
    if (bitbayDownload.status_code == 200):

        bitbayJson = bitbayDownload.json()
        value = 0
        depth = 0

        try:
            while (ammount > 0):
                if ( ammount >= bitbayJson['bids'][depth][1]):
                    ammount -= bitbayJson['bids'][depth][1]
                    value += bitbayJson['bids'][depth][1] * bitbayJson['bids'][depth][0]
                    depth += 1
                else:
                    value += ammount * bitbayJson['bids'][depth][0]
                    ammount = 0
        except:
            return None

        return CurrencyChange.change('USD', value*(1-BITBAY_TAKER_FEE), baseCurrency)