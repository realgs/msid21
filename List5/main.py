import json
import math
from collections import deque
from tkinter import END

from tabulate import tabulate
import APIs.API_list
import finalGui
import StockData.dataKeys

APIS = APIs.API_list.APIS
PROFIT_TAX = 0.19
PORTFOLIO_PATH = 'StockData/wallet.json'
ASSET_TYPES = StockData.dataKeys.ASSET_TYPES
DATA_KEYS = StockData.dataKeys.DATA_KEYS
GUI = finalGui.Gui()


def loadJsonFromFile(path):
    with open(path) as file:
        return json.load(file)


def saveToJson(path, assets):
    file = open(path, 'w')
    json.dump(assets, file, ensure_ascii=False, indent=4)


def convertToBaseCurrency(currency):
    return APIS['currency']['NBP'].ticker(currency, BASE_CURRENCY)['rate']


def calculateCost(quantity, rate, apiName, txFee):
    return float(rate) * (float(quantity) * (1 + float(apiName.takerFee)) + float(txFee))


def calculateProfitArbitrage(quantity, rate, apiName):
    return float(rate) * float(quantity) * (1 - float(apiName.takerFee))


def calculateMinRateQuantity(buy, sell, transferFee, takerFee, api):
    quantity = (min(float(buy['quantity']) + transferFee, float(sell[api.quantity])))
    rate = (float(sell[api.rate]) - float(buy['rate'])) * (1 - float(takerFee))
    return {'rate': rate, 'quantity': quantity}


def calculateDifferenceInPercents(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def getMarketsForArbitrage(assetSymbol):
    markets = []
    for investment in WALLET['assets']['cryptocurrency']:
        if investment['name'] == assetSymbol:
            pass
        else:
            market = f'{assetSymbol}-{investment["name"]}'
            markets.append(market)
    return markets


def calculateProfit(api, assetSymbol, currency, avgPrice, currentVolume):
    conversionRate = 1
    if currency != BASE_CURRENCY:
        conversionRate = convertToBaseCurrency(currency)
    market = f"{assetSymbol.upper()}-{currency.upper()}"

    orderbook = api.orderbook(market)
    if orderbook is None:
        ticker = api.ticker(market)
        if ticker is None:
            return {}
        tickerPrice = ticker['rate']
        return (tickerPrice - avgPrice) * currentVolume * conversionRate

    if orderbook != 0:
        queue = deque(orderbook['bid'])
        profit = 0
        transferFee = api.transferFee(assetSymbol)
        takerFee = api.takerFee
        while currentVolume > 0 and len(queue) > 0:
            bidOffer = queue.pop()
            minRateQuantity = calculateMinRateQuantity(
                {'rate': avgPrice, 'quantity': float(currentVolume)}, bidOffer, transferFee, takerFee, api)
            profit += minRateQuantity['rate'] * minRateQuantity['quantity']
            currentVolume -= abs(min(float(currentVolume), float(bidOffer[api.quantity])))
        return profit * conversionRate
    else:
        return None


def getBestProfit(apiType, assetSymbol, currency, price, quantity):
    profits = []
    for api in APIS[apiType]:
        profit = calculateProfit(
            APIS[apiType][api], assetSymbol, currency, price, quantity)
        if profit is not None:
            profits.append([profit, APIS[apiType][api]])

    profits.sort(key=lambda x: x[0], reverse=True)
    return {'name': profits[0][1].name, 'profit': profits[0][0]}


def calculateArbitrage(currency, api1, api2):
    api1_orderbook = api1.orderbook(currency)
    api2_orderbook = api2.orderbook(currency)
    if api1_orderbook == 0 or api2_orderbook == 0:
        return None
    bids_api1 = api1_orderbook['bid']
    asks_api2 = api2_orderbook['ask']

    i, j, askVolume, bidVolume, cost, profit, temp = 0, 0, 0, 0, 0, 0, 0
    if not asks_api2 or not bids_api1:
        return 0, currency
    else:
        for ask in asks_api2:
            if float(ask[api2.rate]) < float(bids_api1[0][api1.rate]):
                askVolume += float(ask[api2.quantity])
                i += 1
        for bid in bids_api1:
            if float(bid[api1.rate]) > float(asks_api2[i - 1][api2.rate]):
                bidVolume += float(bid[api1.quantity])
                j += 1
        finalAsks = asks_api2[:i]
        finalBids = bids_api1[:j]

        volumeDifference = float(abs(askVolume - bidVolume))
        finalAsks.sort(key=lambda x: abs(float(x[api2.quantity]) - volumeDifference))
        while len(finalAsks) > 0 and askVolume - float(finalAsks[0][api2.quantity]) > bidVolume:
            askVolume -= float(finalAsks[0][api2.quantity])
            finalAsks = finalAsks[1:]

        finalBids.sort(key=lambda x: abs(float(x[api1.quantity]) - volumeDifference))
        while askVolume < bidVolume:
            bidVolume -= float(finalBids[0][api1.quantity])
            finalBids = finalBids[1:]

        leftoverVolume = askVolume - bidVolume
        currency = currency.split('-')[0]
        txFeeAsk = api2.transferFee(currency)

        if not finalAsks or not finalBids:
            cost += calculateCost(asks_api2[0][api2.quantity], asks_api2[0][api2.rate], api2, txFeeAsk)
            profit += calculateProfitArbitrage(bids_api1[0][api1.quantity], bids_api1[0][api1.rate], api1)
            leftoverVolume = float(asks_api2[0][api2.quantity]) - float(bids_api1[0][api1.quantity])
            leftoverValue = leftoverVolume * float(asks_api2[0][api2.rate])
            baseIncome = profit + leftoverValue - cost

            return {'fromTo': f'{api2.name}-{api1.name}',
                    'profit': baseIncome.__round__(4)}
        else:
            for ask in finalAsks:
                cost += calculateCost(ask[api2.quantity], ask[api2.rate], api2, txFeeAsk)
            for bid in finalBids:
                profit += calculateProfitArbitrage(bid[api1.quantity], bid[api1.rate], api1)

            leftoverValue = leftoverVolume * float(finalBids[0][api1.rate])
            baseIncome = profit + leftoverValue - cost

            return {'fromTo': f'{api2.name}-{api1.name}',
                    'profit': baseIncome.__round__(4)}


def getBestArbitrage(assetSymbol):
    possibleArbitrage = [{'market': '---', 'fromTo': '---',
                          'profit': -math.inf}]
    markets = getMarketsForArbitrage(assetSymbol)
    for market in markets:
        print(f'Market: {market}')
        for api_from in APIS['cryptocurrency']:
            for api_to in APIS['cryptocurrency']:
                if api_to != api_from:
                    arbitrage = calculateArbitrage(market, APIS['cryptocurrency'][api_from],
                                                   APIS['cryptocurrency'][api_to])
                    if arbitrage is not None:
                        possibleArbitrage.append({'market': market,
                                                  'fromTo': arbitrage['fromTo'],
                                                  'profit': arbitrage['profit']})
    possibleArbitrage.sort(key=lambda x: x['profit'], reverse=True)
    return possibleArbitrage[0]


def getWallet(investments):
    table = []
    headers = ['Asset type', 'Name', 'Volume', 'Average price', 'Currency']
    for investmentType in investments['assets']:
        for investment in investments['assets'][investmentType]:
            table.append([
                investmentType,
                investment['name'],
                investment['avg_price'],
                investment['volume'],
                investment['currency'],
            ])
    print(tabulate(table, headers=headers, tablefmt="github"))
    return tabulate(table, headers=headers, tablefmt="github")


def getPortfolio(wallet, percent=10):
    table = []
    headers = ["Symbol", "Average price", "Volume", "API", "Profit", "Profit netto", f"Profit {percent}%",
               f"Profit {percent}% netto", "Arbitrage"]
    profitSum, profitSumPercent = 0, 0

    for assetType in wallet['assets']:
        for asset in wallet['assets'][assetType]:
            bestProfit = getBestProfit(assetType, asset['name'], asset['currency'], float(asset['avg_price']),
                                       float(asset['volume']))
            bestProfitPercent = getBestProfit(assetType, asset['name'], asset['currency'], float(asset['avg_price']),
                                              float(asset['volume']) * 0.01 * percent)

            if assetType == 'cryptocurrency':
                bestArbitrage = getBestArbitrage(asset['name'])
                arbitragePrint = f"{bestArbitrage['market']} : {bestArbitrage['fromTo']} : " \
                                 f"{bestArbitrage['profit']} {asset['name']}"
            else:
                arbitragePrint = f'----------'

            table.append([
                asset['name'],
                asset['avg_price'],
                asset['volume'],
                bestProfit['name'],
                f"{bestProfit['profit']:.2f} {BASE_CURRENCY}",
                f"{(bestProfit['profit'] * (1 - PROFIT_TAX)):.2f} {BASE_CURRENCY}",
                f"{bestProfitPercent['profit']:.2f} {BASE_CURRENCY}",
                f"{(bestProfitPercent['profit'] * (1 - PROFIT_TAX)):.2f} {BASE_CURRENCY}",
                arbitragePrint
            ])
            profitSum += float(bestProfit['profit'])
            profitSumPercent += float(bestProfitPercent['profit'])

    table.append(['Sum', '---', '---', '---', f"{profitSum:.2f} {BASE_CURRENCY}",
                  f"{(profitSum * (1 - PROFIT_TAX)):.2f} {BASE_CURRENCY}", f"{profitSumPercent:.2f} {BASE_CURRENCY}",
                  f"{(profitSumPercent * (1 - PROFIT_TAX)):.2f} {BASE_CURRENCY}", '---'])

    print(tabulate(table, headers=headers, tablefmt="github"))
    return tabulate(table, headers=headers, tablefmt="github")


def updateResources(assetType, assetName, quantity, avg_price, currency, path=PORTFOLIO_PATH):
    newAsset = {DATA_KEYS[0]: assetName, DATA_KEYS[1]: quantity, DATA_KEYS[2]: avg_price, DATA_KEYS[3]: currency}
    for asset in WALLET['assets'][assetType]:
        if asset[DATA_KEYS[0]] == assetName:
            WALLET['assets'][assetType].remove(asset)
            break
    if newAsset['volume'] > 0:
        WALLET['assets'][assetType].append(newAsset)
    saveToJson(path, WALLET)


def addAssetToWallet():
    assetType = GUI.assetType.get()
    assetName = GUI.asset.get()
    currency = GUI.currency.get()
    try:
        volume = float(GUI.volume.get())
        avg_price = float(GUI.price.get())
        if volume < 0 or avg_price < 0:
            raise ValueError
        updateResources(assetType, assetName, volume, avg_price, currency)
        pushWalletToGui()
    except ValueError:
        finalGui.throwError('Error', 'Wrong asset data!')


def pushWalletToGui():
    GUI.buttonShowWallet['state'] = 'disable'
    try:
        table = getWallet(WALLET)
    except Exception:
        table = 'No access to wallet!'
    GUI.text.insert(END, '\n')
    GUI.text.insert(END, table)
    GUI.text.insert(END, '\n')
    GUI.buttonShowWallet['state'] = 'normal'


def pushPortfolioToGui():
    GUI.buttonShowPortfolio['state'] = 'disable'
    try:
        percent = int(GUI.percent.get())
        if not (0 < percent <= 100):
            raise ValueError
    except ValueError:
        finalGui.throwError('Error', 'Wrong percent number!')
        percent = 10
    try:
        portfolio = getPortfolio(WALLET, percent)
    except Exception:
        portfolio = 'No access to portfolio'
    GUI.text.insert(END, '\n')
    GUI.text.insert(END, portfolio)
    GUI.text.insert(END, '\n')
    GUI.buttonShowPortfolio['state'] = 'normal'


def initializeGui():
    finalGui.configButtonCommand(GUI.buttonAdd, addAssetToWallet)
    finalGui.configButtonCommand(GUI.buttonShowPortfolio, pushPortfolioToGui)
    finalGui.configButtonCommand(GUI.buttonShowWallet, pushWalletToGui)
    GUI.mainloop()


WALLET = loadJsonFromFile(PORTFOLIO_PATH)
BASE_CURRENCY = WALLET['base_currency']

if __name__ == '__main__':
    initializeGui()
