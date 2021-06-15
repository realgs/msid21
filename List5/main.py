import json
import math
from collections import deque
from tabulate import tabulate
import APIs.API_list
import finalGui
import StockData.dataKeys

APIS = APIs.API_list.APIS
PROFIT_TAX = 0.19
PORTFOLIO_PATH = 'StockData/portfolio.json'
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


def calculateDifference(buy, sell, withdrawalFee, transactionFee, api):
    quantity = (min(float(buy['quantity']), float(sell[api.quantity]) - withdrawalFee))
    return {'rate': (float(sell[api.rate]) - float(buy['rate'])) * (1 - float(transactionFee)), 'quantity': quantity}


def calculateDifferenceInPercents(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def calculateProfit(api, assetSymbol, currency, price, quantity):
    conversionMultiplier = 1
    if currency != 'PLN':
        conversionMultiplier = convertToBaseCurrency(currency)
        print(f'Conversion multiplier: {conversionMultiplier}')
    market = f"{assetSymbol.upper()}-{currency.upper()}"
    print(f'Market: {market} Api: {api.name}')

    orderbook = api.orderbook(market)
    print(f'Orderbook: {orderbook}')
    if orderbook is None:
        ticker = api.ticker(market)
        print(f'Ticker: {ticker}')
        if ticker is None:
            return {}

        tickerPrice = ticker['rate']
        print(f'Ticker price: {tickerPrice}')
        return (tickerPrice - price) * quantity * conversionMultiplier
    elif orderbook != 0:
        queue = deque(
            sorted(orderbook['bid'], key=lambda order1: order1[api.rate]))
        profit = 0
        transferFee = api.transferFee(assetSymbol)
        takerFee = api.takerFee
        while quantity > 0 and len(queue) > 0:
            order = queue.pop()
            difference = calculateDifference(
                {'rate': price, 'quantity': float(quantity)},
                order,
                transferFee,
                takerFee,
                api
            )
            if difference['quantity'] < 0 and difference['rate'] < 0:
                profit -= difference['rate'] * difference['quantity']
            else:
                profit += difference['rate'] * difference['quantity']
            quantity -= abs(min(float(quantity), float(order[api.quantity])))

        return profit * conversionMultiplier


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


def getBestArbitrage(assetSymbol, investments):
    possibleArbitrage = [{'market': '---', 'fromTo': '---',
                          'profit': -math.inf}]
    markets = getMarketsForArbitrage(assetSymbol, investments)
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


def getMarketsForArbitrage(assetSymbol, investments):
    markets = []
    for investment in investments['assets']['cryptocurrency']:
        if investment['name'] == assetSymbol:
            pass
        else:
            market = f'{assetSymbol}-{investment["name"]}'
            markets.append(market)
    return markets


def getPortfolio(investments, percent=10):
    toPrint = []
    headers = ["Symbol", "Average price", "Volume", "Exchange",
               "Profit", "Profit netto", f"Profit {percent}%", f"Profit {percent}% netto", "Arbitrage"]

    sumToPrint = ["Sum", "---", "---", "---", 0, 0, 0, 0, "---"]

    for assetType in investments['assets']:
        for asset in investments['assets'][assetType]:
            bestProfit = getBestProfit(assetType, asset['name'], asset['currency'],
                                       float(asset['avg_price']), float(asset['volume']))

            bestProfitPercent = getBestProfit(assetType, asset['name'], asset['currency'],
                                              float(asset['avg_price']),
                                              float(asset['volume']) * 0.01 * percent)

            if assetType == 'cryptocurrency':
                bestArbitrage = getBestArbitrage(asset['name'], investments)

                arbitragePrint = f"{bestArbitrage['market']} : {bestArbitrage['fromTo']} : " \
                                 f"{bestArbitrage['profit']} {asset['name']}"
            else:
                arbitragePrint = f'----------'

            toPrint.append([
                asset['name'],
                asset['avg_price'],
                asset['volume'],
                bestProfit['name'],
                f"{bestProfit['profit']:.2f}zł",
                f"{(bestProfit['profit'] * (1 - PROFIT_TAX)):.2f}zł",
                f"{bestProfitPercent['profit']:.2f}zł",
                f"{(bestProfitPercent['profit'] * (1 - PROFIT_TAX)):.2f}zł",
                arbitragePrint
            ])

            sumToPrint[4] += float(bestProfit['profit'])
            sumToPrint[5] += float(bestProfit['profit'] * 0.81)
            sumToPrint[6] += float(bestProfitPercent['profit'])
            sumToPrint[7] += float(bestProfitPercent['profit'] * 0.81)

    toPrint.append([sumToPrint[0], sumToPrint[1], sumToPrint[2], sumToPrint[3],
                    f"{sumToPrint[4]:.2f}zł", f"{sumToPrint[5]:.2f}zł", f"{sumToPrint[6]:.2f}zł",
                    f"{sumToPrint[7]:.2f}zł", sumToPrint[8]])

    print(tabulate(toPrint, headers=headers, tablefmt="github"))
    return tabulate(toPrint, headers=headers, tablefmt="github")


def updateResources(resource_type, name, quantity, avg_price, curr, path=PORTFOLIO_PATH):
    old_resources = loadJsonFromFile(path)
    new_resource = {DATA_KEYS[0]: name, DATA_KEYS[1]: quantity, DATA_KEYS[2]: avg_price, DATA_KEYS[3]: curr}
    for resource in old_resources['assets'][resource_type]:
        if resource[DATA_KEYS[0]] == name:
            old_resources['assets'][resource_type].remove(resource)
            break
    if new_resource['volume'] > 0:
        old_resources['assets'][resource_type].append(new_resource)
    saveToJson(path, old_resources)


def addAssetToWallet():
    resource_type = GUI.asset_type.get()
    name = GUI.asset.get()
    currency = GUI.currency.get()
    try:
        quantity = float(GUI.volume.get())
        if quantity < 0:
            raise ValueError
        avg_price = float(GUI.price.get())
        if avg_price < 0:
            raise ValueError
        updateResources(resource_type, name, quantity, avg_price, currency)
        pushWalletToGui()
    except ValueError:
        finalGui.show_error('Error', 'Dane na temat zasobu są niepoprawne')


def pushPortfolioToGui():
    GUI.button_show_portfolio['state'] = 'disable'
    try:
        percent = int(GUI.percent.get())
        if not(0 < percent <= 100):
            raise ValueError
    except ValueError:
        finalGui.show_error('Error', 'Podana wartość procentowa nie jest poprawna')
        percent = 0.1
    GUI.text.insert(1.0, 'Czekaj, trwa odświeżanie portfolio')
    try:
        current_portfolio = getPortfolio(loadJsonFromFile(PORTFOLIO_PATH), percent)
    except Exception:
        current_portfolio = 'Portfolio nie mogło zostać zainicjalizowane'
    GUI.text.delete(1.0, 'end')
    GUI.text.insert(1.0, current_portfolio)
    GUI.button_show_portfolio['state'] = 'normal'


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


def pushWalletToGui():
    table = getWallet(WALLET)
    GUI.text.delete(1.0, 'end')
    GUI.text.insert(1.0, table)


def initializeGui():
    finalGui.set_button_command(GUI.button_add, addAssetToWallet)
    finalGui.set_button_command(GUI.button_show_portfolio, pushPortfolioToGui)
    finalGui.set_button_command(GUI.button_show_wallet, pushWalletToGui)
    GUI.mainloop()


BASE_CURRENCY = loadJsonFromFile(PORTFOLIO_PATH)['base_currency']
WALLET = loadJsonFromFile(PORTFOLIO_PATH)

if __name__ == '__main__':
    # printInvestments(get_json_from_file(PORTFOLIO_PATH), 20)
    initializeGui()

