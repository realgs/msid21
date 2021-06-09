import json
import requests
import pandas as pd
import l4

DEFAULT_PERCENT = 100
APIS = {
    'Currencies': {
        'NBP': "http://api.nbp.pl/api/exchangerates/tables/A/last"
    },
    'Stocks': {
        'Eodhistoricaldata': "https://eodhistoricaldata.com/api/eod/%s"
    }
}


def getEodData(stock='AAPL.US', token='xxxx'):
    url = APIS['Stocks']['Eodhistoricaldata'] % stock + "?api_token=" + token + '&fmt=json'
    response = getDataFromApi(url)
    return response


def getDataFromApi(url):
    headers = {'content-type': "application/json"}
    response = requests.request("GET", url, headers=headers)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        return None


def readWalletResources(fileName):
    walletResources = open(fileName, 'r')
    resourcesData = json.load(walletResources)
    walletResources.close()
    return resourcesData


def getRates():
    rates = getDataFromApi(APIS['Currencies']['NBP'])
    return rates[0]['rates']


def getExchangeRateToPLN(currency):
    rates = getRates()
    rateTo = 0
    for rate in rates:
        if rate['code'] == currency:
            rateTo = rate['mid']
    return rateTo


def getExchangeRateFromPLNToUSD(currency='USD'):
    rates = getRates()
    rateUSD = 0
    for rate in rates:
        if rate['code'] == currency:
            rateUSD = rate['mid']
    return 1 / rateUSD


def showResourcesProfits(dataFrame):
    print(dataFrame)


class Wallet:
    def __init__(self, resourcesFileName):
        self.__resources = readWalletResources(resourcesFileName)
        self.__baseCurrency = self.__resources['Base currency']
        self.__polishStocks = self.__resources['Poland stocks']
        self.__foreignStocks = self.__resources['Foreign stocks']
        self.__currencies = self.__resources['Currencies']
        self.__cryptocurrencies = self.__resources['Cryptocurrencies']

    def sellCurrencies(self, percentOfSell=DEFAULT_PERCENT):
        selledCurrencies = {}
        for currency in self.__currencies:
            selledCurrencies[currency] = []
            quantity = (self.__currencies[currency]['quantity'] * percentOfSell) / 100
            sellRatio = getExchangeRateToPLN(currency)
            if sellRatio is None:
                sellRatio = 1
            profit = quantity * sellRatio
            selledCurrency = {'name': currency, 'quantity': quantity, 'price': sellRatio, 'profit': profit,
                              'profit netto': profit * 0.81}
            selledCurrencies[currency].append(selledCurrency)
        return selledCurrencies

    def getTheBestOffer(self, percentOfSell=DEFAULT_PERCENT):
        soldCurrencies = {}
        for market in l4.TRADE_MARKETS:
            for cryptocurrency in self.__cryptocurrencies:
                soldCurrencies[cryptocurrency] = []
                currencyPair = cryptocurrency + "-" + self.__baseCurrency
                splittedCurrencyPair = currencyPair.split('-')
                sortedBuyOffers = sorted(l4.getOrdersBook(market, currencyPair)['bids'], key=lambda x: x[0],
                                         reverse=True)
                if sortedBuyOffers is None:
                    profit = (self.__cryptocurrencies[cryptocurrency]['quantity'] * percentOfSell) / 100 \
                             * self.__cryptocurrencies[cryptocurrency]['price']
                    soldCurrencies[cryptocurrency].append({'name': cryptocurrency,
                                                           'quantity': self.__cryptocurrencies[cryptocurrency][
                                                               'quantity'],
                                                           'price': self.__cryptocurrencies[cryptocurrency]['price'],
                                                           'profit': profit, 'profit netto': profit * 0.81})
                    break
                withdrawalFeesMarket = l4.getWithdrawalFees(market)
                volumen = (self.__cryptocurrencies[cryptocurrency]['quantity'] * percentOfSell) / 100
                for offer in sortedBuyOffers:
                    if volumen == 0:
                        break
                    transactionVolumen = min(offer[1], volumen)
                    volumeAfterFees = transactionVolumen - withdrawalFeesMarket[market][splittedCurrencyPair[0]]
                    if volumeAfterFees > 0:
                        difference = offer[0] - self.__cryptocurrencies[cryptocurrency]['price']
                        profit = difference * volumeAfterFees
                        if profit > 0:
                            volumen -= volumeAfterFees
                            soldCurrencies[cryptocurrency].append(
                                {'cryptocurrency': cryptocurrency, 'quantity': volumeAfterFees,
                                 'price': offer[0], 'profit': profit, 'profit netto': profit * 0.81})
        return soldCurrencies

    def sellStocks(self, percentOfSell=DEFAULT_PERCENT):
        soldStocks = {}
        exchangeRate = getExchangeRateFromPLNToUSD()
        for stock in self.__polishStocks:
            soldStocks[stock] = []
            stockData = getEodData(stock)
            volumen = (self.__polishStocks[stock]['quantity'] * percentOfSell) / 100
            if stockData is None:
                profit = ((self.__polishStocks[stock]['quantity'] * percentOfSell) / 100 * self.__polishStocks[stock][
                    'price'])
                soldStocks[stock].append(
                    {'stock': stock, 'quantity': volumen, 'price': self.__polishStocks[stock]['price'] * exchangeRate,
                     'profit': profit * exchangeRate, 'profit netto': (profit * 0.81) * exchangeRate})
            else:
                for offer in stockData:
                    if volumen == 0:
                        break
                    transactionVolumen = min(offer['volume'], volumen)
                    difference = offer['close'] - self.__polishStocks[stock]['price']
                    profit = difference * transactionVolumen
                    if profit > 0:
                        volumen -= transactionVolumen
                        soldStocks[stock].append(
                            {'stock': stock, 'quantity': transactionVolumen, 'price': offer['close'] * exchangeRate, 'profit': profit * exchangeRate,
                             'profit netto': (profit * 0.81) * exchangeRate})
        for foreignStock in self.__foreignStocks:
            stockData = getEodData(foreignStock)
            soldStocks[foreignStock] = []
            volumen = (self.__foreignStocks[foreignStock]['quantity'] * percentOfSell) / 100
            if stockData is None:
                profit = ((self.__foreignStocks[foreignStock]['quantity'] * percentOfSell) / 100 *
                          self.__foreignStocks[foreignStock][
                              'price'])
                soldStocks[foreignStock].append(
                    {'stock': foreignStock, 'quantity': volumen, 'price': self.__foreignStocks[foreignStock]['price'],
                     'profit': profit, 'profit netto': profit * 0.81})
            else:
                for offer in stockData:
                    if volumen == 0:
                        break
                    transactionVolumen = min(offer['volume'], volumen)
                    difference = offer['close'] - self.__foreignStocks[foreignStock]['price']
                    profit = difference * transactionVolumen
                    if profit > 0:
                        volumen -= transactionVolumen
                        soldStocks[foreignStock].append({'stock': foreignStock, 'quantity': transactionVolumen,
                                                         'price': offer['close'], 'profit': profit,
                                                         'profit netto': profit * 0.81})
        return soldStocks

    def countSum(self, resources):
        profits = {}
        nettoProfits = {}
        transactionsPrices = {}
        totalProfit = 0
        totalNettoProfit = 0
        for resource in resources.keys():
            sumOfProfit = 0
            sumOfNettoProfit = 0
            lastTransactionPrice = 0
            profits[resource] = 0
            nettoProfits[resource] = 0
            for item in resources[resource]:
                totalProfit += item['profit']
                totalNettoProfit += item['profit netto']
                sumOfProfit += item['profit']
                lastTransactionPrice = item['price']
                sumOfNettoProfit += item['profit netto']
            transactionsPrices[resource] = lastTransactionPrice
            profits[resource] = sumOfProfit
            nettoProfits[resource] = sumOfNettoProfit

        return profits, nettoProfits, transactionsPrices, totalProfit, totalNettoProfit

    def saveSellResourcesToDataFrame(self, percentOfSell=DEFAULT_PERCENT):
        profit = 'Profit ' + str(percentOfSell) + "%"
        profitNetto = 'Netto ' + str(percentOfSell) + '%'
        headersForDataFrame = ['Name', 'Quantity', 'Price', 'Profit', 'Netto', profit, profitNetto]
        soldResources = []

        # currencies
        # all
        soldCurrencies = self.sellCurrencies()
        sumsOfCurrencyProfits = self.countSum(soldCurrencies)
        currencyProfits = sumsOfCurrencyProfits[0]
        currencyNettoProfits = sumsOfCurrencyProfits[1]

        # given percent
        soldCurrencies1 = self.sellCurrencies(percentOfSell)
        sumOfCurrencyPercentProfits = self.countSum(soldCurrencies1)
        currencyPercentProfits = sumOfCurrencyPercentProfits[0]
        currencyPercentNettoProfits = sumOfCurrencyPercentProfits[1]

        # add to table currencies
        for item in soldCurrencies.keys():
            soldResources.append([item, self.__currencies[item]['quantity'], "{:.2f}".format(sumsOfCurrencyProfits[2][item]),
                                  "{:.2f}".format(currencyProfits[item]), "{:.2f}".format(currencyNettoProfits[item]),
                                  "{:.2f}".format(currencyPercentProfits[item]),
                                  "{:.2f}".format(currencyPercentNettoProfits[item])])

        # cryptocurrencies
        # all
        soldCryptocurrencies = self.getTheBestOffer()
        sumsOfCryptocurrencyProfits = self.countSum(soldCryptocurrencies)
        cryptocurrencyProfits = sumsOfCryptocurrencyProfits[0]
        cryptocurrencyNettoProfits = sumsOfCryptocurrencyProfits[1]
        # given percent
        soldCryptocurrencies1 = self.getTheBestOffer(percentOfSell)
        sumOfCryptocurrencyPercentProfits = self.countSum(soldCryptocurrencies1)
        cryptocurrencyPercentProfits = sumOfCryptocurrencyPercentProfits[0]
        cryptocurrencyPercentNettoProfits = sumOfCryptocurrencyPercentProfits[1]

        # add to table cryptocurrencies
        for item in soldCryptocurrencies.keys():
            soldResources.append(
                [item, self.__cryptocurrencies[item]['quantity'], "{:.2f}".format(sumsOfCryptocurrencyProfits[2][item]),
                 "{:.2f}".format(cryptocurrencyProfits[item]), "{:.2f}".format(cryptocurrencyNettoProfits[item]),
                 "{:.2f}".format(cryptocurrencyPercentProfits[item]),
                 "{:.2f}".format(cryptocurrencyPercentNettoProfits[item])])

        # stocks
        # all
        soldStocks = self.sellStocks()
        sumsOfStocksProfits = self.countSum(soldStocks)
        stocksProfits = sumsOfStocksProfits[0]
        stocksNettoProfit = sumsOfStocksProfits[1]

        # given percent
        soldStocks1 = self.sellStocks(percentOfSell)
        sumsOfStocksPercentProfits = self.countSum(soldStocks1)
        stocksPercentProfits = sumsOfStocksPercentProfits[0]
        stocksPercentNettoProfit = sumsOfStocksPercentProfits[1]

        # add to table stocks
        for item in soldStocks.keys():
            if item in self.__foreignStocks:
                quantity = self.__foreignStocks[item]['quantity']
            else:
                quantity = self.__polishStocks[item]['quantity']
            soldResources.append(
                [item, quantity, "{:.2f}".format(sumsOfStocksProfits[2][item]), "{:.2f}".format(stocksProfits[item]),
                 "{:.2f}".format(stocksNettoProfit[item]), "{:.2f}".format(stocksPercentProfits[item]),
                 "{:.2f}".format(stocksPercentNettoProfit[item])])

        sumOfAllProfits = sumsOfStocksProfits[3] + sumsOfCurrencyProfits[3] + sumsOfCryptocurrencyProfits[3]
        sumOfAllNettoProfits = sumsOfStocksProfits[4] + sumsOfCurrencyProfits[4] + sumsOfCryptocurrencyProfits[4]
        sumOfAllPercentProfits = sumsOfStocksPercentProfits[3] + sumOfCurrencyPercentProfits[3] + \
                                 sumOfCryptocurrencyPercentProfits[3]
        sumOfAllPercentNettoProfits = sumsOfStocksPercentProfits[4] + sumOfCurrencyPercentProfits[4] + \
                                      sumOfCryptocurrencyPercentProfits[4]
        soldResources.append(['Sum', '', '', "{:.2f}".format(sumOfAllProfits), "{:.2f}".format(sumOfAllNettoProfits),
                              "{:.2f}".format(sumOfAllPercentProfits), "{:.2f}".format(sumOfAllPercentNettoProfits)])

        resourcesDataFrame = pd.DataFrame(data=soldResources, columns=headersForDataFrame)

        return resourcesDataFrame


if __name__ == '__main__':
    wallet = Wallet('wallet.json')
    dataFrameOfResources = wallet.saveSellResourcesToDataFrame(percentOfSell=50)
    showResourcesProfits(dataFrameOfResources)
