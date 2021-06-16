import requests
import consts
import marketApi
import main
class CryptoMarket(marketApi.Market):
    def __init__(self, name, url, taker, transferFee, bidsName, asksName, dataPath, priceName, volumeName):
        super().__init__(name, consts.CRYPTO["type"])
        self.__url = url
        self.__taker = taker
        self.__transferFee = transferFee
        self.__bidsName = bidsName
        self.__asksName = asksName
        self.__dataPath = dataPath
        self.__priceName = priceName
        self.__volumeName = volumeName
        self.__orderBook = None
        self.__currentCurrencies = None # TODO

    @property        
    def orderBook(self):
        return self.__orderBook

    @property        
    def url(self):
        return self.__url

    def getSellPrice(self, symbol, volume, percentage):
        self.updateOrderBook(symbol, main.WALLET["base currency"])
        if self.isOrderBookFine() == False:
            return -1
        
        return self.getBidPriceFor(volume * percentage / 100)

    def isOrderBookFine(self):
        if self.__orderBook == None:
            return False
        try:
            self.getBestBidPrice()
            return True
        except KeyError:
            return False
        except TypeError:
            return False

    def updateOrderBook(self, baseCur, quoteCur):
        try:
            self.__orderBook = requests.get(self.__url.format(baseCur, quoteCur))
        except requests.exceptions.ConnectionError:
            self.__orderBook = None

    def __obtainData(self, groupName, atName, number):
        if self.__orderBook == None:
            return -1

        json = self.__orderBook.json()
        for step in self.__dataPath:
            json = json[step]

        return round(float(json[groupName][number][atName]), 2)
                
    def getBestBidPrice(self, number = 0):
        return self.__obtainData(self.__bidsName, self.__priceName, number)

    def getBestAskPrice(self, number = 0):
        return self.__obtainData(self.__asksName, self.__priceName, number)

    def getBestBidVolume(self, number = 0):
        return self.__obtainData(self.__bidsName, self.__volumeName, number)
    
    def getBestAskVolume(self, number = 0):
        return self.__obtainData(self.__asksName, self.__volumeName, number)

    def getTaker(self):
        return self.__taker
    
    def getTransferFee(self):
        return self.__transferFee

    # obsluga bledow? w sensie jak sprzedaje wiecej niz jest tam
    def getBidPriceFor(self, volume):
        earn = 0
        number = 0
        while volume > 0:
                temp = min(volume, self.getBestBidVolume(number))
                earn += temp * self.getBestBidPrice(number)
                number += 1
                volume -= temp
        
        return round(earn, 2)
        
class CryptoMarket2(CryptoMarket):
    def updateOrderBook(self, cur1, cur2):
        super().updateOrderBook(cur2, cur1)
        