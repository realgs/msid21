import itertools
import json

from tabulate import tabulate

from FinancePortfolio.api.BitbayApi import BitbayApi
from FinancePortfolio.api.BittrexApi import BittrexApi
from FinancePortfolio.api.NbpApi import NbpApi
from FinancePortfolio.api.EndofdayApi import EndofdayApi

CONFIG_FILE = '../config.json'
BITBAY = BitbayApi()
BITTREX = BittrexApi()
NBP = NbpApi()
EOD = EndofdayApi()
RESOURCE_TYPES = ['cryptocurrencies', 'currencies', 'pl_stock', 'us_stock']
BASE_CURRENCY = ['USD', 'EUR', 'PLN']


def getDataFromFile(file_name):
    with open(file_name) as file:
        data = json.load(file)
    return data


def calculateValue(base_currency, resource_type, symbol, quantity, depth):
    quantity = quantity * depth / 100
    best_exchange = ''
    if resource_type == 'pl_stock':
        price = EOD.getRateInfo(symbol, 'WAR')
        if price is not None:
            if base_currency != 'PLN':
                price = NBP.convertCurrency('PLN', base_currency, price)
            value = quantity * price
            return symbol, quantity, price, value, best_exchange
        else:
            price = 0
            value = 0
            return symbol, quantity, price, value, best_exchange

    elif resource_type == 'us_stock':
        price = EOD.getRateInfo(symbol, 'US')
        if price is not None:
            if base_currency != 'USD':
                price = NBP.convertCurrency('USD', base_currency, price)
            value = quantity * price
            return symbol, quantity, price, value, best_exchange
        else:
            price = 0
            value = 0
            return symbol, quantity, price, value, best_exchange

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
            best_exchange = BITBAY.shortName
        else:
            price = price_bittrex
            best_exchange = BITTREX.shortName
        return symbol, quantity, price, value, best_exchange

    elif resource_type == 'currencies':
        value = NBP.convertCurrency(symbol, base_currency, quantity)
        price = value / quantity
        return symbol, quantity, price, value, best_exchange


def calculateProfit(current_value, cost):
    profit = current_value - cost
    return profit


def calculateNetProfit(profit):
    net_profit = 0.19 * profit  # for polish tax
    return net_profit


def calculateNetValue(average_price, quantity, value, depth):
    if value != 0:
        quantity = quantity * depth / 100
        cost = average_price * quantity
        net_value = value - calculateNetProfit(calculateProfit(value, cost))
        return net_value
    else:
        return 0


def getTable(file, depth):

    table_lines = []

    data = getDataFromFile(file)
    base_currency = data['base_currency']

    resources = list(data.items())
    del resources[0]  # deleting base_currency field
    del resources[0]  # deleting pl_stock
    del resources[0]  # deleting us_stock

    owned_cryptocurrencies = []

    total_value_all = 0
    total_net_value_all = 0
    total_value_depth = 0
    total_net_value_depth = 0

    for resource in resources:
        if resource[0] == 'cryptocurrencies':
            for item in resource[1]:
                owned_cryptocurrencies.append(item['symbol'])
            pairs = list(itertools.permutations(owned_cryptocurrencies, 2))
            markets_intersection = getMarketsIntersection(BITBAY.createMarketsList(), BITTREX.createMarketsList())
            for pair in pairs:
                if f'{pair[0]}-{pair[1]}' in markets_intersection:
                    sell_buy_info = getBuySellInfo(pair[0], pair[1])
                    arbitrage_info = getArbitrageInfo(sell_buy_info, pair[0], pair[1])
                    for i in range(0, len(arbitrage_info)):
                        table_lines.append(['', '', '', '', '', '', '', '', '',
                                            f'{arbitrage_info[i][0]}-{arbitrage_info[i][1]}, '
                                               f'{arbitrage_info[i][3]}-{arbitrage_info[i][4]},'
                                             f' {round(arbitrage_info[i][2], 6)} {arbitrage_info[i][4]}'])
        for item in resource[1]:
            value_all = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], 100)
            net_value_all = calculateNetValue(item['average_price'], item['quantity'], value_all[3], 100)

            value_depth = calculateValue(base_currency, resource[0], item['symbol'], item['quantity'], depth)
            net_value_depth = calculateNetValue(item['average_price'], item['quantity'], value_depth[3], depth)

            total_value_all += round(value_all[3], 2)
            total_net_value_all += round(net_value_all, 2)

            total_value_depth += round(value_depth[3], 2)
            total_net_value_depth += round(net_value_depth, 2)

            table_lines.append([value_all[0], value_all[1],
                            round(value_all[2], 2), round(value_all[3], 2), round(net_value_all, 2), value_depth[4],
                            round(value_depth[3], 2), round(net_value_depth, 2), value_all[4], ''])
    table_lines.append(['Total:', '', '', '%.2f'%total_value_all, '%.2f'%total_net_value_all, '', '%.2f'%total_value_depth,
                        '%.2f'%total_net_value_depth, '', ''])
    return table_lines


def getMarketsIntersection(markets_1, markets_2):
    intersection = []
    for market in markets_1:
        if market in markets_2:
            intersection.append(market)
    return intersection


def calculateDifference(value_1, value_2):
    result = value_1 - value_2 / value_2
    return result


def calculateCost(quantity, rate, fees, currency):
    cost = rate * (quantity + fees['transfer_fee'][currency] + quantity * fees['taker_fee'])
    return cost


def calculateIncome(quantity, rate, fees):
    income = rate * quantity * (1 - fees['taker_fee'])
    return income


def getBuySellInfo(currency_1, currency_2):
    bitbay_info = BITBAY.getBestSellBuy(currency_1, currency_2)
    bittrex_info = BITTREX.getBestSellBuy(currency_1, currency_2)
    if bitbay_info and bittrex_info is not None:
        sell_buy_info = bitbay_info, bittrex_info
        return sell_buy_info
    else:
        return None


def getRateInfo(sell_buy_info):
    bitbay_buy_rate = []
    bitbay_sell_rate = []
    bittrex_buy_rate = []
    bittrex_sell_rate = []

    for element in sell_buy_info[0]:
        bitbay_buy_rate.append(float(element[1]['ra']))
        bitbay_sell_rate.append(float(element[0]['ra']))
    for element in sell_buy_info[1]:
        bittrex_buy_rate.append(float(element[1]['rate']))
        bittrex_sell_rate.append(float(element[0]['rate']))

    return bitbay_buy_rate, bitbay_sell_rate, bittrex_buy_rate, bittrex_sell_rate


def getQuantityInfo(sell_buy_info):
    bitbay_buy_quantity = []
    bitbay_sell_quantity = []
    bittrex_buy_quantity = []
    bittrex_sell_quantity = []

    for element in sell_buy_info[0]:
        bitbay_buy_quantity.append(float(element[1]['ca']))
        bitbay_sell_quantity.append(float(element[0]['ca']))
    for element in sell_buy_info[1]:
        bittrex_buy_quantity.append(float(element[1]['quantity']))
        bittrex_sell_quantity.append(float(element[0]['quantity']))
    return bitbay_buy_quantity, bitbay_sell_quantity, bittrex_buy_quantity, bittrex_sell_quantity


def getArbitrageInfo(buy_sell_info, currency_1, currency_2):
    rate_info = getRateInfo(buy_sell_info)
    quantity_info = getQuantityInfo(buy_sell_info)

    arbitrage_quantity_bitbay_bittrex = min(quantity_info[1][0], quantity_info[2][0])
    arbitrage_quantity_bittrex_bitbay = min(quantity_info[3][0], quantity_info[0][0])

    sell_position = 0
    buy_position = 0

    arbitrage_profit_bitbay_bittrex = 0
    arbitrage_profit_bittrex_bitbay = 0

    income_bitbay_bittrex = 0
    income_bittrex_bitbay = 0

    cost_bitbay_bittrex = 0
    cost_bittrex_bitbay = 0

    # buy on bitbay, sell on bittrex
    while sell_position < len(rate_info[2]) and buy_position < len(rate_info[1]) and\
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], BITTREX.fees) > \
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], BITBAY.fees, currency_1):
        if sell_position != 0:
            arbitrage_quantity_bitbay_bittrex += min(quantity_info[1][sell_position], quantity_info[2][sell_position])
        arbitrage_profit_bitbay_bittrex += \
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], BITTREX.fees) -\
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], BITBAY.fees, currency_1)
        income_bitbay_bittrex += \
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], BITTREX.fees)
        cost_bitbay_bittrex += \
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], BITBAY.fees, currency_1)
        if quantity_info[1][sell_position] == quantity_info[2][sell_position]:
            sell_position += 1
            buy_position += 1
        elif quantity_info[1][sell_position] < quantity_info[2][sell_position]:
            buy_position += 1
            quantity_info[2][sell_position] -= quantity_info[1][sell_position]
        elif quantity_info[1][sell_position] > quantity_info[2][sell_position]:
            sell_position += 1
            quantity_info[1][sell_position] -= quantity_info[2][sell_position]

    # buy on bittrex, sell on bitbay
    while sell_position < len(rate_info[0]) and buy_position < len(rate_info[3]) and \
            calculateIncome(arbitrage_quantity_bittrex_bitbay, rate_info[0][sell_position], BITBAY.fees) > \
            calculateCost(arbitrage_quantity_bittrex_bitbay, rate_info[3][buy_position], BITTREX.fees, currency_1):
        if sell_position != 0:
            arbitrage_quantity_bitbay_bittrex += min(quantity_info[3][sell_position], quantity_info[0][sell_position])
        arbitrage_profit_bittrex_bitbay += \
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[0][sell_position], BITTREX.fees) -\
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[3][buy_position], BITBAY.fees, currency_1)
        income_bittrex_bitbay += \
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[0][sell_position], BITTREX.fees)
        cost_bittrex_bitbay += \
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[3][buy_position], BITBAY.fees, currency_1)
        if quantity_info[3][sell_position] == quantity_info[0][sell_position]:
            sell_position += 1
            buy_position += 1
        elif quantity_info[3][sell_position] < quantity_info[0][sell_position]:
            buy_position += 1
            quantity_info[0][sell_position] -= quantity_info[3][sell_position]
        elif quantity_info[3][sell_position] > quantity_info[0][sell_position]:
            sell_position += 1
            quantity_info[3][sell_position] -= quantity_info[0][sell_position]

    if arbitrage_profit_bitbay_bittrex == 0:
        income_bitbay_bittrex = calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][0], BITTREX.fees)
        cost_bitbay_bittrex = calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][0], BITBAY.fees, currency_1)
        arbitrage_profit_bitbay_bittrex = income_bitbay_bittrex - cost_bitbay_bittrex

    if arbitrage_profit_bittrex_bitbay == 0:
        income_bittrex_bitbay = calculateIncome(arbitrage_quantity_bittrex_bitbay, rate_info[0][0], BITBAY.fees)
        cost_bittrex_bitbay = calculateCost(arbitrage_quantity_bittrex_bitbay, rate_info[3][0], BITTREX.fees, currency_1)
        arbitrage_profit_bittrex_bitbay = income_bittrex_bitbay - cost_bittrex_bitbay

    info_bitbay_bittrex = BITBAY.shortName, BITTREX.shortName, arbitrage_profit_bitbay_bittrex, currency_1, currency_2
    info_bittrex_bitbay = BITTREX.shortName, BITBAY.shortName, arbitrage_profit_bittrex_bitbay, currency_1, currency_2
    return info_bitbay_bittrex, info_bittrex_bitbay
