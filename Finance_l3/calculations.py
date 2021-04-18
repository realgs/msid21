import bitbay

import bittrex

currencies = ["BTC", "USD"]
names = [bitbay.NAME, bittrex.NAME]


def calculateDifference(value_1, value_2):
    result = (1 - (value_1 - value_2) / value_2) * 100
    return result


def calculateCost(quantity, rate, fees):
    cost = rate * (quantity + fees['transfer_fee_btc'] + quantity * fees['taker_fee'])
    return cost


def calculateProfit(quantity, rate, fees):
    profit = rate * quantity * (1 - fees['taker_fee'])
    return profit


def getBuySellInfo():
    bitbay_info = bitbay.getBestSellBuy(currencies[0], currencies[1])
    bittrex_info = bittrex.getBestSellBuy(currencies[1], currencies[0])
    buy_sell_info = bitbay_info, bittrex_info
    return buy_sell_info


def getRateInfo(buy_sell_info):
    bitbay_buy_rate = float(buy_sell_info[0][1]['ra'])
    bitbay_sell_rate = float(buy_sell_info[0][0]['ra'])
    bittrex_buy_rate = float(buy_sell_info[1][1]['Rate'])
    bittrex_sell_rate = float(buy_sell_info[1][0]['Rate'])
    return bitbay_buy_rate, bitbay_sell_rate, bittrex_buy_rate, bittrex_sell_rate


def getQuantityInfo(buy_sell_info):
    bitbay_buy_quantity = float(buy_sell_info[0][1]['ca'])
    bitbay_sell_quantity = float(buy_sell_info[0][0]['ca'])
    bittrex_buy_quantity = float(buy_sell_info[1][1]['Quantity'])
    bittrex_sell_quantity = float(buy_sell_info[1][0]['Quantity'])
    return bitbay_buy_quantity, bitbay_sell_quantity, bittrex_buy_quantity, bittrex_sell_quantity


def printSellBuyInfo(buy_sell_info):
    bitbay.printBestSellBuy(buy_sell_info[0][0], buy_sell_info[0][1], currencies[0], currencies[1])
    bittrex.printBestSellBuy(buy_sell_info[1][0], buy_sell_info[1][1], currencies[1], currencies[0])


def printIsProfitable(cost, profit):
    if profit > cost:
        print('Arbitrage is profitable')
    else:
        print('Arbitrage is not profitable')
    print(f'The profit is {calculateDifference(profit, cost)}% which is {profit - cost} {currencies[1]}')


def printDifferences(buy_sell_info):
    rate_info = getRateInfo(buy_sell_info)
    print(f'\nSelling difference is {calculateDifference(rate_info[1], rate_info[3])}%')
    print(f'Buying difference is {calculateDifference(rate_info[0], rate_info[2])}%')
    print(f'Buying on {names[0]} and selling on {names[1]} difference is {calculateDifference(rate_info[1], rate_info[2])}%')
    print(f'Buying on {names[1]} and selling on {names[0]} difference is {calculateDifference(rate_info[3], rate_info[0])}%\n')


def printOptionInfo(name_1, name_2, arbitrage_quantity, cost, profit):
    print(f'\nArbitrage info for buying on {name_1} and selling on {name_2}: ')
    print(f'Quantity of currency that can be arbitraged: {arbitrage_quantity}')
    printIsProfitable(cost, profit)


def printArbitrageInfo(buy_sell_info):
    rate_info = getRateInfo(buy_sell_info)
    quantity_info = getQuantityInfo(buy_sell_info)

    arbitrage_quantity_bitbay_bittrex = min(quantity_info[1], quantity_info[2])
    arbitrage_quantity_bittrex_bitbay = min(quantity_info[3], quantity_info[0])

    profit_sell_bittrex = calculateProfit(arbitrage_quantity_bitbay_bittrex, rate_info[2], bittrex.BITTREX_FEES)
    cost_buy_bitbay = calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1], bitbay.BITBAY_FEES)

    profit_sell_bitbay = calculateProfit(arbitrage_quantity_bittrex_bitbay, rate_info[0], bitbay.BITBAY_FEES)
    cost_buy_bittrex = calculateCost(arbitrage_quantity_bittrex_bitbay, rate_info[3], bittrex.BITTREX_FEES)

    printOptionInfo(names[0], names[1], arbitrage_quantity_bitbay_bittrex, cost_buy_bitbay, profit_sell_bittrex)
    printOptionInfo(names[1], names[0], arbitrage_quantity_bittrex_bitbay, cost_buy_bittrex, profit_sell_bitbay)
