from apis.api import Api
import yfinance as yf

class Yahoo(Api):

    def __init__(self):
        self.cmp = yf.Ticker("")

    def getData(self, url: str):
        pass

    def connect(self):
        pass

    def getField(self, json, i, action):
        pass

    def getOrdersNumber(self, json):
        pass

    def getTicker(self):
        pass

    def getPrice(self, company):
        self.cmp = yf.Ticker(company)
        print(float(self.cmp.info["bid"]))
