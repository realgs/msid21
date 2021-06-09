import yfinance as yf

class Yahoo():

    def __init__(self):
        self.cmp = yf.Ticker("")

    def getSellRate(self):
        return self.getPrice()

    def getPrice(self, company):
        self.cmp = yf.Ticker(company)
        return float(self.cmp.info["bid"])
