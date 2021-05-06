from collections import deque

from api.apis import APIS


def findCommonMarkets(api1, api2):
    results = []

    api1Markets = api1.markets
    api2Markets = api2.markets

    for market in api1Markets:
        if market in api2Markets:
            results.append(market)

    return results


def calculateDifference(orderFrom, orderTo, apiFrom, apiTo, symbol):
    quantity = min(orderFrom['quantity'], orderTo['quantity']) * (1 - apiTo.transactionFee) - apiFrom.withdrawalFee(symbol)

    return {
        'rate': (orderFrom['rate'] - orderTo['rate']),
        'quantity': quantity
    }


def calculateProfit(apiFrom, apiTo, symbol):
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

        difference = calculateDifference(orderFrom, orderTo, apiFrom, apiTo, currency)
        
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
        return (previousProfit * quantity) / rateSum * -100
    elif rateSum != 0:
        return (previousProfit * quantity) / rateSum * 100

    return 0


def main():

    # Ex1
    print("Ex1: ")
    commonMarkets = findCommonMarkets(APIS['BITBAY'], APIS['BITTREX'])
    print(commonMarkets)

    # Ex2
    print("Ex2: ")
    print(
        f"BTC-USD:\t{calculateProfit(APIS['BITBAY'], APIS['BITTREX'], 'BTC-USD'):.4f}%")
    print(
        f"ETH-USD:\t{calculateProfit(APIS['BITBAY'], APIS['BITTREX'], 'ETH-USD'):.4f}%")
    print(
        f"LTC-USD:\t{calculateProfit(APIS['BITBAY'], APIS['BITTREX'], 'LTC-USD'):.4f}%")

    # Ex3
    print("Ex3: ")
    profits = []
    for market in commonMarkets:
        profits.append((market, calculateProfit(APIS['BITBAY'], APIS['BITTREX'], market)))

    profits = sorted(profits, key=lambda el: float(el[1]), reverse=True)

    for profit in profits:
        print(f"{profit[0]}:\t{profit[1]:.4f} %")


if __name__ == "__main__":
    main()
