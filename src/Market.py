import requests

class Market:
    def __init__(self, name, url, taker, transferFee, bidsName, asksName, dataPath, priceName, volumeName):
        self.__name = name
        self.__url = url
        self.__taker = taker
        self.__transferFee = transferFee
        self.__bidsName = bidsName
        self.__asksName = asksName
        self.__dataPath = dataPath
        self.__priceName = priceName
        self.__volumeName = volumeName
        # self.__orderBook = requests.get(self.__url)

    def updateOrderBook(self):
        try:
            self.__orderBook = requests.get(self.__url)
        except requests.exceptions.ConnectionError:
            self.__orderBook = None

    def __obtainData(self, groupName, atName):
        if self.__orderBook == None:
            return -1

        json = self.__orderBook.json()
        for step in self.__dataPath:
            json = json[step]
            
        return float(json[groupName][0][atName])

    def getLastBidPrice(self):
        return self.__obtainData(self.__bidsName, self.__priceName)

    def getLastAskPrice(self):
        return self.__obtainData(self.__asksName, self.__priceName)

    def getLastBidVolume(self):
        return self.__obtainData(self.__bidsName, self.__volumeName)
    
    def getLastAskVolume(self):
        return self.__obtainData(self.__asksName, self.__volumeName)

    def getTaker(self):
        return self.__taker
    
    def getTransferFee(self):
        return self.__transferFee