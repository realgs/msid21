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
def calculateValue(base_currency, resource_type, symbol, quantity):

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
        price_bitbay = BITBAY.getLastBuyOfferPrice(symbol, base_currency)
        price_bittrex = BITTREX.getLastBuyOfferPrice(symbol, base_currency)
        value_bitbay = BITBAY.getResourceValue(symbol, base_currency, quantity)
        value_bittrex = BITTREX.getResourceValue(symbol, base_currency, quantity)
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


# test
if __name__ == "__main__":
    data = getDataFromConfigFile()
    resources = list(data.items())
    del resources[0] # deleting base_currency field
    #del resources[0] # deleting pl_stock
    #del resources[0] # deleting us_stock
    #print(resources)

    base_currency = data['base_currency']
    #print(base_currency)

    print("{:<8} {:<15} {:<30} {:<15}".format('Name', 'Quantity', 'Price (last transaction)', 'Value'))
    print('----------------------------------------------------------------------')

    total_value = 0

    for resource in resources:
        for item in resource[1]:
            value = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'])
            if value[3] != "-":
                total_value += value[3]
            print("{:<8} {:<15} {:<30} {:<15}".format(value[0], value[1], value[2], value[3]))
    print("{:<56} {:<5}".format('\nTotal value of owned resources:', total_value))
