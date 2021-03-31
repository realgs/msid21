import bitbay
import bittrex

# TODO: Check fee policy
FIRST_API_NAME = "Bittrex"
# FIRST_MARKET_TAKER_FEE = 0.0025
# FIRST_MARKET_TRANSFER_FEE = 0.0025
FIRST_MARKET_FEE = 0.0025
SECOND_API_NAME = "Bitbay"
# SECOND_MARKET_TAKER_FEE = 0.001
# SECOND_MARKET_TRANSFER_FEE = 0.001
SECOND_MARKET_FEE = 0.001

def _getBuyRate(firstApiData, secondApiData):
    firstApiBuy = firstApiData['buy']['price']
    secondApiBuy = secondApiData['buy']['price']
    return firstApiBuy / secondApiBuy * 100


def displayBuyRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        rate = _getBuyRate(bestBittrex, bestBitbay)
        print("Sell rate: ")
        print(f"{FIRST_API_NAME} / {SECOND_API_NAME} = {rate}%")
    else:
        print("The rate cannot be calculated")


def _getSellRate(firstApiData, secondApiData):
    firstApiSell = firstApiData['sell']['price']
    secondApiSell = secondApiData['sell']['price']
    return firstApiSell / secondApiSell * 100


def displaySellRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        rate = _getBuyRate(bestBittrex, bestBitbay)
        print("Sell rate: ")
        print(f"{FIRST_API_NAME} / {SECOND_API_NAME} = {rate}%")
    else:
        print("The rate cannot be calculated")


def _getCrossProfitRate(firstApiData, secondApiData):
    firstApiBuyPrice = firstApiData['buy']['price']  # bittrexBuyPrice
    firstApiBuyQuantity = firstApiData['buy']['quantity']  # bittrexBuyQuantity
    firstApiSellPrice = firstApiData['sell']['price']  # bittrexSellPrice
    firstApiSellQuantity = firstApiData['sell']['quantity']  # bittrexSellQuantity
    secondApiBuyPrice = secondApiData['buy']['price']  # bitbayBuyPrice
    secondApiBuyQuantity = secondApiData['buy']['quantity']  # bitbayBuyQuantity
    secondApiSellPrice = secondApiData['sell']['price']  # bitbaySellPrice
    secondApiSellQuantity = secondApiData['sell']['quantity']  # bitbaySellQuantity

    rate1 = firstApiBuyPrice * (1 - FIRST_MARKET_FEE) / secondApiSellPrice * (1 - SECOND_MARKET_FEE)
    quantity1 = min(firstApiBuyQuantity, secondApiSellQuantity)
    profit1 = (rate1 - 1)

    rate2 = secondApiBuyPrice * (1 - SECOND_MARKET_FEE) / firstApiSellPrice * (1 - FIRST_MARKET_FEE)
    quantity2 = min(secondApiBuyQuantity, firstApiSellQuantity)
    profit2 = (rate2 - 1) * quantity2

    return rate1 * 100, quantity1, profit1, rate2 * 100, quantity2, profit2


def displayCrossProfitRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        rate1, quantity1, profit1, rate2, quantity2, profit2 = _getCrossProfitRate(bestBittrex, bestBitbay)
        print("Profit percentage (100% - 0 profit):")
        print(f"Buy in {FIRST_API_NAME}, sell in {SECOND_API_NAME}: {rate1},\t Profit: {profit1} {cryptos[1]}")
        print(f"Buy in {SECOND_API_NAME}, sell in {FIRST_API_NAME}: {rate2},\t Profit: {profit2} {cryptos[1]}")
    else:
        print("The profit rate cannot be calculated")


def displayMarketsDifferenceRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        print("Buy rate: ")
        print(f"{FIRST_API_NAME} / {SECOND_API_NAME} = {_getBuyRate(bestBittrex, bestBitbay)}%", end="\n\n")
        print("Sell rate: ")
        print(f"{FIRST_API_NAME} / {SECOND_API_NAME} = {_getSellRate(bestBittrex, bestBitbay)}%", end="\n\n")
        rate1, quantity1, profit1, rate2, quantity2, profit2 = _getCrossProfitRate(bestBittrex, bestBitbay)
        print("Profit percentage (100% - 0 profit):")
        rate1Fixed = "{:.6f}".format(rate1)
        print(f"Buy in {FIRST_API_NAME}, sell in {SECOND_API_NAME}\t\tRate: {rate1Fixed},\t\tQuantity: {quantity1},"
              f"\t\tFull profit: {profit1} {cryptos[1]}")
        rate2Fixed = "{:.6f}".format(rate2)
        print(f"Buy in {SECOND_API_NAME}, sell in {FIRST_API_NAME}\t\tRate: {rate2Fixed},\t\tQuantity: {quantity2},"
              f"\t\tFull profit: {profit2} {cryptos[1]}")
    else:
        print("The rate cannot be calculated")
