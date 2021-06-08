import CurrencyChange

DEFAULT_DEPTH = 15

BITTREX_ORDER_URL_PREFIX = 'https://api.bittrex.com/v3/markets/'
BITTREX_ORDER_URL_POSTFIX = '/orderbook'
BITTREX_TAKER_FEE = 0.0035

class BitTrex():
    def __init__(self):
        self.name = 'BitTrex'
        self.resourcesTables = {}

    def getName(self):
        return self.name

    def getResourceBidAskTable(self, resource, new=False):
        if (self.resourcesTables.keys().__contains__(resource) and not new):
            return self.resourcesTables[resource]

        try:
            result = {'bid': [], 'ask': []}

            bittrexDownload = requests.get(BITTREX_ORDER_URL_PREFIX + resource + '-USD' + BITTREX_ORDER_URL_POSTFIX)

            if (bittrexDownload.status_code == 200):
                bittrexJson = bittrexDownload.json()

            for depth in range(DEFAULT_DEPTH):
                result['bid'].append([float(bittrexJson['bid'][depth]['rate']), float(bittrexJson['bid'][depth]['quantity'])])
                result['ask'].append([float(bittrexJson['ask'][depth]['rate']), float(bittrexJson['ask'][depth]['quantity'])])

            self.resourcesTables[resource] = result
            return result

        except:
            return None

    def sell(self, resource, ammount, baseCurrency='USD'):
        table = self.getResourceBidAskTable(resource)

        depth = 0
        value = 0
        while (ammount > 0):
            if (table['bid'][depth][1] >= ammount):
                value += ammount * table['bid'][depth][0]
                ammount = 0
            else:
                value += table['bid'][depth][0] * table['bid'][depth][1]
                ammount -= table['bid'][depth][1]
            depth += 1

        value *= (1-BITTREX_TAKER_FEE)

        return round(CurrencyChange.change('USD', value, baseCurrency), 2)

    def lastMaxPrice(self, resource, baseCurrency='USD'):
        data = self.getResourceBidAskTable(resource)
        return round(CurrencyChange.change('USD', data['bid'][0][0], baseCurrency), 2)
