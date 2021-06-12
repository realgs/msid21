from Finance_l4 import bitbay, bittrex

names = [bitbay.NAME, bittrex.NAME]


def getMarketsIntersection(markets_1, markets_2):
    intersection = []
    for market in markets_1:
        if market in markets_2:
            intersection.append(market)
    return intersection


def calculateDifference(value_1, value_2):
    result = (1 - (value_1 - value_2) / value_2) * 100
    return result


def calculateCost(quantity, rate, fees, currency):
    cost = rate * (quantity + fees['transfer_fee'][currency] + quantity * fees['taker_fee'])
    return cost


def calculateIncome(quantity, rate, fees):
    income = rate * quantity * (1 - fees['taker_fee'])
    return income


def getBuySellInfo(currency_1, currency_2):
    bitbay_info = bitbay.getBestSellBuy(currency_1, currency_2)
    bittrex_info = bittrex.getBestSellBuy(currency_2, currency_1)
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
        bittrex_buy_rate.append(float(element[1]['Rate']))
        bittrex_sell_rate.append(float(element[0]['Rate']))

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
        bittrex_buy_quantity.append(float(element[1]['Quantity']))
        bittrex_sell_quantity.append(float(element[0]['Quantity']))
    return bitbay_buy_quantity, bitbay_sell_quantity, bittrex_buy_quantity, bittrex_sell_quantity


def printOptionInfo(name_1, name_2, arbitrage_quantity, income, cost, profit, currency_1, currency_2):
    print(f'\nArbitrage info for buying on {name_1} and selling on {name_2} for market {currency_1}-{currency_2}:')
    if profit > 0:
        print(f'Quantity of currency that can be arbitraged: {arbitrage_quantity}')
        print(f'The profit is {calculateDifference(income, cost)}% which is {profit} {currency_2}')
    else:
        print('Arbitrage is not profitable')
        print(f'The profit is {calculateDifference(income, cost)}% which is {profit} {currency_2}')


def printArbitrageInfo(info):
    printOptionInfo(info[0][0], info[0][1], info[0][2], info[0][3], info[0][4], info[0][5], info[0][6], info[0][7])
    printOptionInfo(info[1][0], info[1][1], info[1][2], info[1][3], info[1][4], info[1][5], info[1][6], info[1][7])


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
    while sell_position < len(rate_info[2]) and buy_position < len (rate_info[1]) and\
            calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], bittrex.BITTREX_FEES) > \
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], bitbay.BITBAY_FEES, currency_1):
        if sell_position != 0:
            arbitrage_quantity_bitbay_bittrex += min(quantity_info[1][sell_position], quantity_info[2][sell_position])
        arbitrage_profit_bitbay_bittrex += calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], bittrex.BITTREX_FEES) -\
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], bitbay.BITBAY_FEES, currency_1)
        income_bitbay_bittrex += calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][sell_position], bittrex.BITTREX_FEES)
        cost_bitbay_bittrex += calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][buy_position], bitbay.BITBAY_FEES, currency_1)
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
            calculateIncome(arbitrage_quantity_bittrex_bitbay, rate_info[0][sell_position], bitbay.BITBAY_FEES) > \
            calculateCost(arbitrage_quantity_bittrex_bitbay, rate_info[3][buy_position], bittrex.BITTREX_FEES, currency_1):
        if sell_position != 0:
            arbitrage_quantity_bitbay_bittrex += min(quantity_info[3][sell_position], quantity_info[0][sell_position])
        arbitrage_profit_bittrex_bitbay += calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[0][sell_position], bittrex.BITTREX_FEES) -\
            calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[3][buy_position], bitbay.BITBAY_FEES, currency_1)
        income_bittrex_bitbay += calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[0][sell_position], bittrex.BITTREX_FEES)
        cost_bittrex_bitbay += calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[3][buy_position], bitbay.BITBAY_FEES, currency_1)
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
        income_bitbay_bittrex = calculateIncome(arbitrage_quantity_bitbay_bittrex, rate_info[2][0], bittrex.BITTREX_FEES)
        cost_bitbay_bittrex = calculateCost(arbitrage_quantity_bitbay_bittrex, rate_info[1][0], bitbay.BITBAY_FEES, currency_1)
        arbitrage_profit_bitbay_bittrex = income_bitbay_bittrex - cost_bitbay_bittrex

    if arbitrage_profit_bittrex_bitbay == 0:
        income_bittrex_bitbay = calculateIncome(arbitrage_quantity_bittrex_bitbay, rate_info[0][0], bitbay.BITBAY_FEES)
        cost_bittrex_bitbay = calculateCost(arbitrage_quantity_bittrex_bitbay, rate_info[3][0], bittrex.BITTREX_FEES, currency_1)
        arbitrage_profit_bittrex_bitbay = income_bittrex_bitbay - cost_bittrex_bitbay

    info_bittbay_bittrex = names[0], names[1], arbitrage_quantity_bitbay_bittrex, income_bitbay_bittrex, cost_bitbay_bittrex , arbitrage_profit_bitbay_bittrex, currency_1, currency_2
    info_bittrex_bitbay = names[1], names[0], arbitrage_quantity_bittrex_bitbay, income_bittrex_bitbay, cost_bittrex_bitbay, arbitrage_profit_bittrex_bitbay, currency_1, currency_2
    return info_bittbay_bittrex, info_bittrex_bitbay
