import bitbay
import bittrex
import time
from _datetime import datetime

# TODO: Check fee policy
FIRST_API_NAME = "Bittrex"
# FIRST_MARKET_TAKER_FEE = 0.0025
# FIRST_MARKET_TRANSFER_FEE = 0.0025
FIRST_MARKET_FEE = 0.0025
SECOND_API_NAME = "Bitbay"
# SECOND_MARKET_TAKER_FEE = 0.001
# SECOND_MARKET_TRANSFER_FEE = 0.001
SECOND_MARKET_FEE = 0.001


def _displayBuyRate(firstApiData, secondApiData):
    firstApiBuy = firstApiData['buy']['price']
    secondApiBuy = secondApiData['buy']['price']
    rateFixed = "{:.6f}".format(firstApiBuy / secondApiBuy * 100)
    print(f"Buy rate: {FIRST_API_NAME} / {SECOND_API_NAME} = {rateFixed} %")


def displayBuyRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayBuyRate(bestBittrex, bestBitbay)
    else:
        print("The rate cannot be calculated")


def _displaySellRate(firstApiData, secondApiData):
    firstApiSell = firstApiData['sell']['price']
    secondApiSell = secondApiData['sell']['price']
    rateFixed = "{:.6f}".format(firstApiSell / secondApiSell * 100)
    print(f"Sell rate: {FIRST_API_NAME} / {SECOND_API_NAME} = {rateFixed} %")


def displaySellRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayBuyRate(bestBittrex, bestBitbay)
    else:
        print("The rate cannot be calculated")


def _displayCrossProfitRate(firstApiData, secondApiData, currency):
    firstApiBuy = firstApiData['buy']  # bittrexBuy
    firstApiSell = firstApiData['sell']  # bittrexSell
    secondApiBuy = secondApiData['buy']  # bitbayBuy
    secondApiSell = secondApiData['sell']  # bitbaySell

    rate1 = firstApiBuy['price'] * (1 - FIRST_MARKET_FEE) / secondApiSell['price'] * (1 - SECOND_MARKET_FEE)
    quantity1 = min(firstApiBuy['quantity'], secondApiSell['quantity'])
    profit1 = (rate1 - 1)

    rate2 = secondApiBuy['price'] * (1 - SECOND_MARKET_FEE) / firstApiSell['price'] * (1 - FIRST_MARKET_FEE)
    quantity2 = min(secondApiBuy['price'], firstApiSell['quantity'])
    profit2 = (rate2 - 1) * quantity2

    rate1Fixed = "{:.6f}".format(rate1 * 100)
    rate2Fixed = "{:.6f}".format(rate2 * 100)
    quantity1Fixed = "{:.6f}".format(quantity1)
    quantity2Fixed = "{:.6f}".format(quantity2)

    print("Profit percentage (100% - 0 profit):")
    print(f"Buy in {FIRST_API_NAME}, sell in {SECOND_API_NAME}\t\tRate: {rate1Fixed},\t\tQuantity: {quantity1Fixed},"
          f"\t\tFull profit: {profit1} {currency}")
    print(f"Buy in {SECOND_API_NAME}, sell in {FIRST_API_NAME}\t\tRate: {rate2Fixed},\t\tQuantity: {quantity2Fixed},"
          f"\t\tFull profit: {profit2} {currency}")


def displayCrossProfitRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayCrossProfitRate(bestBittrex, bestBitbay, cryptos[1])
    else:
        print("The profit rate cannot be calculated")


def displayMarketsDifferenceRateStream(cryptos, interval=5):
    while True:
        print("\n", datetime.now().strftime("%H:%M:%S"))
        bestBittrex = bittrex.getBestOrders(cryptos)
        bestBitbay = bitbay.getBestOrders(cryptos)

        if bestBittrex['success'] and bestBitbay['success']:
            _displayBuyRate(bestBittrex, bestBitbay)
            _displaySellRate(bestBittrex, bestBitbay)
            _displayCrossProfitRate(bestBittrex, bestBitbay, cryptos[1])
        else:
            print("The rate cannot be calculated")
            break
        time.sleep(interval)
