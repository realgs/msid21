import CurrencyChange
import yfinance as yf

DEFAULT_DEPTH = 10
DEFAULT_AMMOUNT = 9999

class Yahoo():
    def __init__(self):
        self.name = 'Yahoo'

    def getName(self):
        return self.name


    def getResourceBidAskTable(self, resource):
        try:
            result = {'bid':[], 'ask':[]}
            stock = yf.Ticker(resource)

            for i in range(DEFAULT_DEPTH):
                result['bid'].append([float(stock.info['bid']), DEFAULT_AMMOUNT])
                result['ask'].append([float(stock.info['ask']), DEFAULT_AMMOUNT])

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

        return round( CurrencyChange.change('USD', value, baseCurrency), 2)

    def lastMaxPrice(self, resource, baseCurrency='USD'):
        data = self.getResourceBidAskTable(resource)
        return round(CurrencyChange.change('USD', data['bid'][0][0], baseCurrency), 2)
