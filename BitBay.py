import requests
import CurrencyChange

DEFAULT_DEPTH = 15

BITBAY_ORDER_URL_PREFIX = 'https://bitbay.net/API/Public/'
BITBAY_ORDER_URL_POSTFIX = '/orderbook.json'
BITBAY_TAKER_FEE = 0.0042

class BitBay():
    def __init__(self):
        self.name = 'BitBay'
        self.resourcesTables = {}

    def getName(self):
        return self.name

    def getResourceBidAskTable(self, resource, new=False):
        if ( self.resourcesTables.keys().__contains__(resource) and not new ):
            return self.resourcesTables[resource]

        try:
            result = {'bid':[], 'ask':[]}
            bitbayDownload = requests.get(BITBAY_ORDER_URL_PREFIX + resource + 'USD' + BITBAY_ORDER_URL_POSTFIX)

            if (bitbayDownload.status_code == 200):
                bitbayJson = bitbayDownload.json()

            for depth in range(DEFAULT_DEPTH):
                result['bid'].append([float(bitbayJson['bids'][depth][0]), bitbayJson['bids'][depth][1]])
                result['ask'].append([float(bitbayJson['asks'][depth][0]), bitbayJson['asks'][depth][1]])

            self.resourcesTables[resource] = result
            return result

        except:
            return None


    def sell(self, resource, ammount, baseCurrency='USD'):
        table = self.getResourceBidAskTable(resource)

        depth = 0
        value = 0
        while ( ammount > 0):
            if ( table['bid'][depth][1] >= ammount ):
                value += ammount * table['bid'][depth][0]
                ammount = 0
            else:
                value += table['bid'][depth][0] * table['bid'][depth][1]
                ammount -= table['bid'][depth][1]
            depth += 1

        value *= (1-BITBAY_TAKER_FEE)

        return round( CurrencyChange.change('USD', value, baseCurrency), 2)

    def lastMaxPrice(self, resource, baseCurrency='USD'):
        data = self.getResourceBidAskTable(resource)
        return round(CurrencyChange.change('USD', data['bid'][0][0], baseCurrency), 2)
