import requests

import CurrencyChange

BITTREX_ORDER_URL_PREFIX = 'https://api.bittrex.com/v3/markets/'
BITTREX_ORDER_URL_POSTFIX = '/orderbook'
BITTREX_TAKER_FEE = 0.0035

def value(resource, ammount, baseCurrency):

    bittrexDownload = requests.get(BITTREX_ORDER_URL_PREFIX + resource + '-USD' + BITTREX_ORDER_URL_POSTFIX)
    if (bittrexDownload.status_code == 200):

        bittrexJson = bittrexDownload.json()
        value = 0
        depth = 0

        try:
            while (ammount > 0):
                if ( ammount >= float(bittrexJson['bid'][depth]['quantity'])):
                    ammount -= float(bittrexJson['bid'][depth]['quantity'])
                    value += float(bittrexJson['bid'][depth]['quantity']) * float(bittrexJson['bid'][depth]['rate'])
                    depth += 1
                else:
                    value += ammount * float(bittrexJson['bid'][depth]['rate'])
                    ammount = 0
        except:
            return None


        return CurrencyChange.change('USD', value*(1-BITTREX_TAKER_FEE), baseCurrency)