from apis.api import Api

API = "https://bitbay.net/API/Public/{}{}/orderbook.json"

class Bitbay(Api):
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

    def sellCrypto(self, crypto):
        pass