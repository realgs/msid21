import requests

class TradePair:
    def __init__(self, name, currencies, url, taker, transferFee, bidsName, asksName, dataPath, priceName, volumeName):
        self.__name = name
        self.__currencies = currencies
        self.__url = url
        self.__taker = taker
        self.__transferFee = transferFee
        self.__bidsName = bidsName
        self.__asksName = asksName
        self.__dataPath = dataPath
        self.__priceName = priceName
        self.__volumeName = volumeName
        self.__orderBook = None

    def isOrderBookFine(self):
        return self.__orderBook != None

    def updateOrderBook(self):
        try:
            self.__orderBook = requests.get(self.__url)
        except requests.exceptions.ConnectionError:
            self.__orderBook = None

    def __obtainData(self, groupName, atName, number):
        if self.__orderBook == None:
            return -1

        json = self.__orderBook.json()
        for step in self.__dataPath:
            json = json[step]
            
        return float(json[groupName][number][atName])

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

    def getName(self):
        return self.__name

    def getCurrencies(self):
        return self.__currencies