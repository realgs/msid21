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


def _printFullInfo(buyIn, sellIn, rate, quantity, profit, currency):
    rateFixed = "{:.6f}".format(rate * 100)
    quantityFixed = "{:.6f}".format(quantity)
    if profit > 0:
        colorPrefix, colorSuffix = '\x1b[6;30;42m', '\x1b[0m'
    else:
        colorPrefix, colorSuffix = '\x1b[6;30;41m', '\x1b[0m'
    print(f"{colorPrefix}Buy in {buyIn}, sell in {sellIn}\t\tRate: {rateFixed},"
          f"\t\tQuantity: {quantityFixed},\t\tFull profit: {profit} {currency}{colorSuffix}")


def _displayCrossProfitRate(firstApiData, secondApiData, currency):
    firstApiBuy, firstApiSell = firstApiData['buy'], firstApiData['sell']
    secondApiBuy, secondApiSell = secondApiData['buy'], secondApiData['sell']

    rate1, quantity1, profit1 = _getTransactionData(firstApiBuy, secondApiSell)
    rate2, quantity2, profit2 = _getTransactionData(secondApiBuy, firstApiSell)

    print("Profit percentage (100% - 0 profit):")
    _printFullInfo(FIRST_API_NAME, SECOND_API_NAME, rate1, quantity1, profit1, currency)
    _printFullInfo(SECOND_API_NAME, FIRST_API_NAME, rate2, quantity2, profit2, currency)


def displayCrossProfitRate(cryptos):
    bestBittrex = bittrex.getBestOrders(cryptos)
    bestBitbay = bitbay.getBestOrders(cryptos)

    if bestBittrex['success'] and bestBitbay['success']:
        _displayCrossProfitRate(bestBittrex, bestBitbay, cryptos[1])
    else:
        print("The profit rate cannot be calculated")


def displayMarketsDifferenceRateStream(allCryptos, interval=5):
    while True:
        for cryptos in allCryptos:
            print("\n", datetime.now().strftime("%H:%M:%S"), f"{cryptos[0]} -> {cryptos[1]}")
            bestBittrex = bittrex.getBestOrders(cryptos)
            bestBitbay = bitbay.getBestOrders(cryptos)

            if bestBittrex['success'] and bestBitbay['success']:
                _displayBuyRate(bestBittrex, bestBitbay)
                _displaySellRate(bestBittrex, bestBitbay)
                _displayCrossProfitRate(bestBittrex, bestBitbay, cryptos[1])
            else:
                print("The rate cannot be calculated")
                return
        time.sleep(interval)
