from Data.TableData import TableData
import json

WALLET_FILE = "wallet.json"
DEFAULT_BASE_CURRENCY = "USD"


class DataManager:
    def __init__(self, serviceDataProvider):
        self.serviceDataProvider = serviceDataProvider
        self.walletData = dict()
        self.availableMarkets = dict()
        self.commonMarkets = set()

    def loadData(self):
        try:
            with open(WALLET_FILE, "r") as jsonFile:
                data = json.load(jsonFile)
                self.walletData = data
                return True
        finally:
            self.commonMarkets = set()
            return False

    def saveData(self):
        try:
            with open(WALLET_FILE, "w") as jsonFile:
                json.dump(self.walletData, jsonFile)
                return True
        finally:
            return False

    def loadMarkets(self):
        for service in self.serviceDataProvider.getRegisteredServicesNames():
            self.availableMarkets[service] = self.serviceDataProvider.fetchNormalizedMarkets(
                service)

    def isWalletEmpty(self):
        return not self.walletData.__contains__("wallet")

    def createTableData(self):
        tableData = TableData()
        tableData.headers = ["Service", "Currency",
                             "Amount", "Rate", "Price", "Price 10%", "Best at"]
        if self.isWalletEmpty():
            return tableData

        baseCurrency = self.walletData['baseCurrency']
        for service in self.walletData['wallet']:
            if self.serviceDataProvider.isRegistered(service):
                stock = self.walletData['wallet'][service]
                for currency in stock:
                    amount = 0
                    for buyRecord in stock[currency]:
                        amount += buyRecord['amount']

                    bestPrice = 0
                    bestPrice10 = 0
                    soldAt = ""
                    for regService in self.serviceDataProvider.getRegisteredServicesNames():
                        market = (currency, baseCurrency)
                        if self.availableMarkets[regService].__contains__(market):
                            orderbook = self.serviceDataProvider.fetchNormalizedOrderBook(
                                regService, market)
                            tempRate, tempPrice = self.calculatePrice(amount, orderbook.buyOffers)
                            if tempPrice > bestPrice:
                                bestPrice = tempPrice
                                soldAt = regService
                                temp, bestPrice10 = self.calculatePrice(amount * 0.1, orderbook.buyOffers)
                    tableData.addRow([service, currency, str(amount), str(tempRate), str(bestPrice), str(bestPrice10), soldAt])
            else:
                print("Service is not registered")

        return tableData

    def calculatePrice(self, amount, buys):
        price = 0
        remainingAmount = float(amount)
        i = 0
        lastRate = 0
        while remainingAmount > 0 and i < len(buys):
            buy = buys[i]
            canSell = min(float(buy.amount), remainingAmount)
            price += canSell * float(buy.rate)
            lastRate = float(buy.rate)
            remainingAmount -= canSell
            i += 1

        return lastRate, price

    def getAvailableServices(self):
        return self.serviceDataProvider.getRegisteredServicesNames()

    def addNewStock(self, service, stock, amount, rate):
        if not 'wallet' in self.walletData:
            self.walletData["baseCurrency"] = DEFAULT_BASE_CURRENCY
            self.walletData["wallet"] = dict()

        wallet = self.walletData['wallet']
        if not service in wallet:
            wallet[service] = dict()

        if not stock in wallet[service]:
            wallet[service][stock] = list()

        wallet[service][stock].append(
            {'amount': amount, 'rate': rate}
        )
