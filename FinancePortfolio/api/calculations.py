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


# task 2
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


# test task 2,3
if __name__ == "__main__":
    data = getDataFromConfigFile()
    resources = list(data.items())
    del resources[0] # deleting base_currency field
    #del resources[0] # deleting pl_stock
    #del resources[0] # deleting us_stock
    #print(resources)

    base_currency = data['base_currency']
    #depth = int(input('Enter percentage to calculate: '))
    depth = 10

    print("{:<8} {:<30} {:<30} {:<30} {:<15}".format('Name', 'Quantity', 'Price (last transaction)', 'Value', f'Value {depth}%'))
    print('-' * 150)

    total_value_all = 0
    total_value_depth = 0

    for resource in resources:
        for item in resource[1]:
            value_all = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], 100)
            value_depth = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], depth)
            if value_all[3] != "-":
                total_value_all += value_all[3]
            if value_depth[3] != "-":
                total_value_depth += value_depth[3]
            print("{:<8} {:<30} {:<30} {:<30}".format(value_all[0], value_all[1], value_all[2], value_all[3]),
                  value_depth[3])
    print("{:<71} {:<5}".format('\nTotal value of owned resources:', total_value_all))
    print("{:<101} {:<5}".format(f'Total value of {depth}% of owned resources:', total_value_depth))
