import requests
import enum

TRADE_MARKETS = ['bitbay', 'bittrex']
MARKETS_URL = ['https://bitbay.net/API/Public/', 'https://api.bittrex.com/v3/markets/']
TAKER_FEES = {
    'bitbay': 0.001,
    'bittrex': 0.0025
}
TRANSFER_FEES = {
    'bitbay': {
        'BTC': 0.0005,
        'LTC': 0.001,
        'ETH': 0.01,
        'DASH': 0.001
    },
    'bittrex': {
        'BTC': 0.0005,
        'LTC': 0.01,
        'ETH': 0.006,
        'DASH': 0.05
    }
}
CRYPTO_CURRENCIES = ['BTC', 'LTC', 'ETH', 'DASH']
BASE_CURRENCY = 'USD'

OPERATIONS = enum.Enum('BUY', 'SELL', 'ARBITRATION')

def getDataFromApi(url):
    response = requests.get(url)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        return None


def getSellBuyOffers(exchangeMarket, cypto, curency, offersLimit):
    if exchangeMarket == TRADE_MARKETS[0]:
        tradeOffers = getDataFromApi(MARKETS_URL[0] + cypto + curency + '/orderbook.json')
        offers = {'bids': tradeOffers['bids'][:offersLimit], 'asks': tradeOffers['asks'][:offersLimit]}
        if offers is not None:
            return offers
    elif exchangeMarket == TRADE_MARKETS[1]:
        tradeOffers = getDataFromApi(MARKETS_URL[1] + cypto + '-' + curency + '/orderbook')
        sellOffers = []
        buyOffers = []
        for bids in tradeOffers['bid'][:offersLimit]:
            buyOffers.append([float(bids['rate']), float(bids['quantity'])])
        for asks in tradeOffers['ask'][:offersLimit]:
            sellOffers.append([float(asks['rate']), float(asks['quantity'])])
        offers = {'bids': buyOffers, 'asks': sellOffers}
        if offers is not None:
            return offers
    return None


def findPriceDifference(tradeOffer1, tradeOffer2):


def calculatePriceDifference(exchangeMarket, crypto, currency, offersLimit, delayOfExploringData, operation):
 while True:
      tradeOffer1 = getSellBuyOffers(exchangeMarket, crypto, currency, offersLimit)
      tradeOffer2 = getSellBuyOffers(exchangeMarket, crypto, currency, offersLimit)

     if operation == OPERATIONS.BUY:
          findPriceDifference(tradeOffer1, tradeOffer2)
     elif operation == OPERATIONS.SELL:
            findPriceDifference(tradeOffer1, tradeOffer2)


getSellBuyOffers(TRADE_MARKETS[0], 'BTC', 'USD', 10);
getSellBuyOffers(TRADE_MARKETS[1], 'BTC', 'USD', 10);
