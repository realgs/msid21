import json

from FinancePortfolio.api.BitbayApi import BitbayApi
from FinancePortfolio.api.BittrexApi import BittrexApi
from FinancePortfolio.api.NbpApi import NbpApi
from FinancePortfolio.api.EndofdayApi import EndofdayApi

CONFIG_FILE = 'config.json'
BITBAY = BitbayApi()
BITTREX = BittrexApi()
NBP = NbpApi()
EOD = EndofdayApi()


def getDataFromConfigFile():
    with open(CONFIG_FILE) as file:
        data = json.load(file)
    return data


def calculateValue(base_currency, resource_type, symbol, quantity, depth):
    quantity = quantity * depth / 100

    if resource_type == 'pl_stock':
        price = EOD.getRateInfo(symbol, 'WAR')
        if price is not None:
            if base_currency != 'PLN':
                price = NBP.convertCurrency('PLN', base_currency, price)
            value = quantity * price
            return symbol, quantity, price, value
        else:
            price = "-"
            value = "-"
            return symbol, quantity, price, value

    elif resource_type == 'us_stock':
        price = EOD.getRateInfo(symbol, 'US')
        if price is not None:
            if base_currency != 'USD':
                price = NBP.convertCurrency('USD', base_currency, price)
            value = quantity * price
            return symbol, quantity, price, value
        else:
            price = "-"
            value = "-"
            return symbol, quantity, price, value

    elif resource_type == 'cryptocurrencies':
        result_bitbay = BITBAY.getResourceValue(symbol, base_currency, quantity)
        value_bitbay = result_bitbay[0]
        price_bitbay = result_bitbay[1]

        result_bittrex = BITTREX.getResourceValue(symbol, base_currency, quantity)
        value_bittrex = result_bittrex[0]
        price_bittrex = result_bittrex[1]

        value = max(value_bitbay, value_bittrex)

        if value == value_bitbay:
            price = price_bitbay
        else:
            price = price_bittrex
        return symbol, quantity, price, value

    elif resource_type == 'currencies':
        value = NBP.convertCurrency(symbol, base_currency, quantity)
        price = value / quantity
        return symbol, quantity, price, value


def calculateProfit(current_value, cost):
    profit = current_value - cost
    return profit


def calculateNetProfit(profit):
    net_profit = 0.19 * profit  # for polish tax
    return net_profit


def calculateNetValue(average_price, quantity, value, depth):
    quantity = quantity * depth / 100
    cost = average_price * quantity
    net_value = value - calculateNetProfit(calculateProfit(value, cost))
    return net_value


def displayTable():
    data = getDataFromConfigFile()
    base_currency = data['base_currency']

    resources = list(data.items())
    del resources[0]  # deleting base_currency field
    del resources[0]  # deleting pl_stock
    del resources[0]  # deleting us_stock

    #depth = int(input('Enter percentage to calculate: '))
    depth = 10  # value for testing

    print("{:<8} {:<30} {:<30} {:<30} {:<30} {:<30} {:<30}".format('Name', 'Quantity', 'Price (last transaction)',
                                                     'Value', 'Net value', f'Value {depth}%', f'Net value {depth}%'))
    print('-' * 200)

    total_value_all = 0
    total_net_value_all = 0
    total_value_depth = 0
    total_net_value_depth = 0

    for resource in resources:
        for item in resource[1]:
            value_all = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], 100)
            net_value_all = calculateNetValue(item['average_price'], item['quantity'], value_all[3], 100)
            value_depth = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], depth)
            net_value_depth = calculateNetValue(item['average_price'], item['quantity'], value_depth[3], depth)

            if value_all[3] != "-":
                total_value_all += value_all[3]
            total_net_value_all += net_value_all
            if value_depth[3] != "-":
                total_value_depth += value_depth[3]
            total_net_value_depth += net_value_depth
            print("{:<8} {:<30} {:<30} {:<30} {:<30} {:<30} {:<30}".format(value_all[0], value_all[1], value_all[2],
                                                        value_all[3], net_value_all, value_depth[3], net_value_depth))
    print("{:<71} {:<5}".format('\nTotal value of owned resources:', total_value_all))
    print("{:<101} {:<5}".format('Total net value of owned resources:', total_net_value_all))
    print("{:<132} {:<5}".format(f'Total value of {depth}% of owned resources:', total_value_depth))
    print("{:<163} {:<5}".format(f'Total net value of {depth}% of owned resources:', total_net_value_depth))


# test task 2,3,4
if __name__ == "__main__":
    displayTable()


