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


def _displayRate(firstApiData, secondApiData, source, message):
    firstApiBuy = firstApiData[source]['price']
    secondApiBuy = secondApiData[source]['price']
    rateFixed = "{:.6f}".format(firstApiBuy / secondApiBuy * 100)
    print(f"{message}: {FIRST_API_NAME} / {SECOND_API_NAME} = {rateFixed} %")


def _displayBuyRate(firstApiData, secondApiData):
    _displayRate(firstApiData, secondApiData, 'buy', 'Buy rate')


def displayBuyRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayBuyRate(bestBittrex, bestBitbay)
    else:
        print("The rate cannot be calculated")


def _displaySellRate(firstApiData, secondApiData):
    _displayRate(firstApiData, secondApiData, 'sell', 'Sell rate')


def displaySellRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayBuyRate(bestBittrex, bestBitbay)
    else:
        print("The rate cannot be calculated")


def _getTransactionData(buyOrder, sellOrder):
    rate = buyOrder['price'] * (1 - FIRST_MARKET_FEE) / sellOrder['price'] * (1 - SECOND_MARKET_FEE)
    quantity = min(buyOrder['quantity'], sellOrder['quantity'])
    profit = (rate - 1) * quantity
    return rate, quantity, profit


def _displayCrossProfitRate(firstApiData, secondApiData, currency):
    firstApiBuy, firstApiSell = firstApiData['buy'], firstApiData['sell']
    secondApiBuy, secondApiSell = secondApiData['buy'], secondApiData['sell']

    rate1, quantity1, profit1 = _getTransactionData(firstApiBuy, secondApiSell)
    rate2, quantity2, profit2 = _getTransactionData(secondApiBuy, firstApiSell)

    rate1Fixed, rate2Fixed = "{:.6f}".format(rate1 * 100), "{:.6f}".format(rate2 * 100)
    quantity1Fixed, quantity2Fixed = "{:.6f}".format(quantity1), "{:.6f}".format(quantity2)

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
