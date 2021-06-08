import requests

NBP_URL_PREFIX = 'http://api.nbp.pl/api/exchangerates/rates/a/'

DEFAULT_DEPTH = 10
DEFAULT_AMMOUNT = 9999

class NBP():
    def __init__(self):
        self.name = 'NBP'
        self.resourcesTables = {}

    def getName(self):
        return self.name


    def getResourceBidAskTable(self, resource, new=False):
        if ( self.resourcesTables.keys().__contains__(resource) and not new ):
            return self.resourcesTables[resource]

        try:
            resource = resource.split('-')
            firstCurrency = resource[0].lower()
            secondCurrency = resource[1].lower()

            result = {'bid':[], 'ask':[]}
            NBPdownloadFirst = requests.get(NBP_URL_PREFIX + firstCurrency + '/')
            NBPdownloadSecond = requests.get(NBP_URL_PREFIX + secondCurrency + '/')

            if (NBPdownloadFirst.status_code == 200 and NBPdownloadSecond.status_code == 200):
                NBPjsonFirst = NBPdownloadFirst.json()
                NBPjsonSecond = NBPdownloadSecond.json()

            price = NBPjsonFirst['rates'][0]['mid'] / NBPjsonSecond['rates'][0]['mid']

            for i in range(DEFAULT_DEPTH):
                result['bid'].append([round(price, 2), DEFAULT_AMMOUNT])
                result['ask'].append([round(price, 2), DEFAULT_AMMOUNT])

            return result

        except:
            return None


    def sell(self, resource, ammount, baseCurrency):
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

        return round( value, 2)


    def lastMaxPrice(self, resource, baseCurrency):
        data = self.getResourceBidAskTable(resource)
        return round(data['bid'][0][0], 2)