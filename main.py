import json
import requests
import math
from collections import deque
from tabulate import tabulate
from api.apis import APIS


def convertToPLN(currency):
    return APIS['Currency']['NBP'].ticker(currency)['price']


def calculateDifference(buy, sell, withdrawalFee, transactionFee):
    quantity = (min(buy['quantity'], sell['quantity']) -
                withdrawalFee)

    return {
        'rate': (sell['rate'] - buy['rate']) * (1 - transactionFee),
        'quantity': quantity
    }


def calculateArbitrage(apiFrom, apiTo, symbol):
    if apiFrom.orderbook != None and apiFrom.orderbook != None:
        queueFrom = deque(apiFrom.orderbook(symbol)['bid'])
        queueTo = deque(apiFrom.orderbook(symbol)['ask'])
        currency = symbol.split('-')[0]

        previousProfit = 0
        profit = None
        quantity = 0
        rateSum = 0

        while (profit == None or profit > 0) and len(queueFrom) > 0 and len(queueTo) > 0:

            # Updating old profit
            if profit != None:
                previousProfit = profit

            # Getting 1st orders from queues
            orderFrom = queueFrom.pop()
            orderTo = queueTo.pop()

            difference = calculateDifference(
                orderFrom, orderTo, apiFrom.withdrawalFee(currency), apiTo.transactionFee)

            if profit == None:
                previousProfit = profit = difference['rate']
                quantity = difference['quantity']
                rateSum = orderFrom['rate']

            if difference['quantity'] > 0:
                profit += difference['rate']
                quantity += difference['quantity']
                rateSum += orderFrom['rate']

            # Putting back order with quantity left
            if orderFrom['quantity'] > orderTo['quantity'] and orderFrom['quantity'] > apiFrom.withdrawalFee(currency):
                queueFrom.append({
                    'quantity': orderFrom['quantity'] - orderTo['quantity'],
                    'rate': orderFrom['rate']
                })
            elif orderFrom['quantity'] < orderTo['quantity'] and orderTo['quantity'] > apiFrom.withdrawalFee(currency):
                queueTo.append({
                    'quantity': orderTo['quantity'] - orderFrom['quantity'],
                    'rate': orderTo['rate']
                })

        if rateSum != 0 and quantity < 0 and previousProfit < 0:
            return (previousProfit * quantity) / rateSum 
        elif rateSum != 0:
            return (previousProfit * quantity) / rateSum

    return -math.inf


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
        queue = deque(
            sorted(orderbook['bid'], key=lambda order: order['rate']))
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
            if(difference['quantity'] < 0 and difference['rate'] < 0):
                profit -= difference['rate'] * difference['quantity']
            else:
                profit += difference['rate'] * difference['quantity']
            quantity -= abs(min(quantity, order['quantity']))

        return profit * conversionMultiplier


def getBestProfit(apiType, symbol, currency, price, quantity, apiName=None, skipCurrentApi=False):
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


def getBestArbitrage(apiType, symbol, currency, apiName):
    profits = [0]

    if apiName != None:
        for api in APIS[apiType]:
            if api == apiName:
                profits.append(-math.inf)
            else:
                profits.append(calculateArbitrage(APIS[apiType][apiName],
                                                  APIS[apiType][api], f"{symbol}-{currency}"))

    maxIndex = profits.index(max(profits))
    return {'name': f"{apiName}-{['---', *list(APIS[apiType].keys())][maxIndex]}", 'profit': profits[maxIndex]}


def loadInvestments():
    file = open(
        '/home/karol/Documents/Projects/Studia/MSID/laboratoria/investments.json')
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

        bestArbitrage = getBestArbitrage(
            investment['type'], investment['symbol'], investment['currency'], api)

        arbitragePrint = bestArbitrage['name'] if bestArbitrage[
            'name'] == f"{api}----" else f"{bestArbitrage['name']}:{bestArbitrage['profit']:.2f}%"

        toPrint.append([
            investment['symbol'],
            investment['pricePerShare'],
            investment['quantity'],
            bestProfit['name'],
            f"{bestProfit['profit']:.2f}zł",
            f"{(bestProfit['profit']*0.81):.2f}zł",
            f"{bestProfit10['profit']:.2f}zł",
            f"{(bestProfit10['profit']*0.81):.2f}zł",
            arbitragePrint
        ])

    print(tabulate(toPrint, headers=headers))


def main():

    printInvestments(loadInvestments())


if __name__ == "__main__":
    main()
