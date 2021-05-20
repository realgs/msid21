import json
import requests
import math
from collections import deque
from tabulate import tabulate
from api.apis import APIS


def convertToPLN(currency):
    return APIS['Currency']['NBP'].ticker(currency)['price']


def calculateDifference(buy, sell, withdrawalFee, transactionFee):
    quantity = min(buy['quantity'], sell['quantity']) * \
        (1 - transactionFee) - withdrawalFee

    return {
        'rate': (sell['rate'] - buy['rate']),
        'quantity': quantity
    }


# Returns profit in PLN
def calculateProfit(api, symbol, currency, price, quantity, transactionFee=0):
    conversionMultiplier = 1
    if currency != 'PLN':
        conversionMultiplier = convertToPLN(currency)
    market = f"{symbol.upper()}-{currency.upper()}"

    orderbook = api.orderbook(market)
    if orderbook == None:
        ticker = api.ticker(market)
        if ticker == None:
            return 0

        tickerPrice = ticker['price']
        return (tickerPrice - price) * quantity * conversionMultiplier
    else:
        queue = deque(orderbook['bid'])
        profit = 0
        withdrawalFee = api.withdrawalFee(symbol)
        while quantity > 0 and len(queue) > 0:
            order = queue.pop()
            difference = calculateDifference(
                {'rate': price, 'quantity': quantity},
                order,
                withdrawalFee,
                transactionFee
            )

            profit += difference['rate'] * difference['quantity']
            quantity -= min(quantity, order['quantity'])

        return profit * conversionMultiplier


def getBestProfit(apiType, symbol, currency, price, quantity, apiName=None, skipCurrentApi = False):
    profits = []
    transactionFee = 0
    if apiName != None:
        transactionFee = APIS[apiType][apiName].transactionFee

    for api in APIS[apiType]:
        if api == apiName and skipCurrentApi == True:
             profits.append(-math.inf)   
        else:
            profits.append(calculateProfit(
                APIS[apiType][api], symbol, currency, price, quantity, transactionFee))
            

    maxIndex = profits.index(max(profits))
    return {'name': list(APIS[apiType].keys())[maxIndex], 'profit': profits[maxIndex]}


def loadInvestments():
    file = open(
        '/home/karol/Documents/Projects/Studia/MSID/laboratoria/investmentsTests.json')
    return json.load(file)


def printInvestments(investments):
    toPrint = []
    headers = ["Symbol", "Cena", "Ilość", "Giełda",
               "Zysk", "Zysk netto", "Zysk 10%", "Zysk 10% netto", "Arbitraż"]
    for investment in investments:

        api = None
        if 'api' in investment:
            api = investment['api']

        bestProfit = getBestProfit(investment['type'], investment['symbol'], investment['currency'],
                               float(investment['pricePerShare']), float(investment['quantity']), api)

        bestProfit10 = getBestProfit(investment['type'], investment['symbol'], investment['currency'],
                               float(investment['pricePerShare']), float(investment['quantity']) * 0.1, api)

        toPrint.append([
            investment['symbol'],
            investment['pricePerShare'],
            investment['quantity'],
            bestProfit['name'],
            f"{bestProfit['profit']:.2f}zł", 
            f"{(bestProfit['profit']*0.81):.2f}zł", 
            f"{bestProfit10['profit']:.2f}zł", 
            f"{(bestProfit10['profit']*0.81):.2f}zł",
            0 # TODO: Arbitraż
        ])

    print(tabulate(toPrint, headers=headers))


def main():
    # print(list(APIS['Crypto'].keys()))
    printInvestments(loadInvestments())


if __name__ == "__main__":
    main()
