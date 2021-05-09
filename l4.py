import requests

TRADE_MARKETS = {'bitbay': 'bitbay',
                 'bittrex': 'bittrex'}
MARKETS_URL = {'bitbay': 'https://api.bitbay.net/rest/trading/ticker',
               'bittrex': 'https://api.bittrex.com/v3/markets/'}
ORDER_BOOKS_URL = {'bitbay': 'https://api.bitbay.net/rest/trading/orderbook/',
                   'bittrex': 'https://api.bittrex.com/v3/markets/'}
ORDER_BOOKS_END_OF_URL = {'bitbay': '',
                          'bittrex': '/orderbook'}
ORDER_BOOKS_CURRENCY_PAIR_SPLIT = {'bitbay': ''}
ORDER_BOOKS_ASKS_OFFERS_NAMES = {'bitbay': 'sell',
                                 'bittrex': 'ask'}
ORDER_BOOKS_BIDS_OFFERS_NAMES = {'bitbay': 'buy',
                                 'bittrex': 'bid'}
ORDER_BOOKS_QUANTITY_OFFERS_NAMES = {'bitbay': 'ca',
                                     'bittrex': 'quantity'}
ORDER_BOOKS_RATE_OFFERS_NAMES = {'bitbay': 'ra',
                                 'bittrex': 'rate'}
MARKETS_CURRENCIES_SYMBOL_NAMES = {'bittrex': 'symbol',
                                   'bitbay': 'items'}
MARKETS_WITHDRAWAL_FEES_URL = {'bittrex': 'https://api.bittrex.com/v3/currencies',
                               'bitbay': ''}

WITHDRAWAL_FEES = {'bitbay': {'AAVE': 0.23,
                                     'ALG': 258.00,
                                     'AMLT': 965.00,
                                     'BAT': 29.00,
                                     'BCC': 0.001,
                                     'BCP': 665.00,
                                     'BOB': 4901.00,
                                     'BSV': 0.003,
                                     'BTC': 0.0005,
                                     'BTG': 0.001,
                                     'COMP': 0.025,
                                     'DAI': 19.00,
                                     'DASH': 0.001,
                                     'DOT': 0.10,
                                     'EOS': 0.10,
                                     'ETH': 0.006,
                                     'EXY': 52.00,
                                     'GAME': 279.00,
                                     'GGC': 6.00,
                                     'GNT': 66.00,
                                     'GRT': 11.00,
                                     'LINK': 1.85,
                                     'LML': 150.00,
                                     'LSK': 0.30,
                                     'LTC': 0.001,
                                     'LUNA': 0.02,
                                     'MANA': 27.00,
                                     'MKR': 0.014,
                                     'NEU': 109.00,
                                     'NPXS': 2240.00,
                                     'OMG': 3.50,
                                     'PAY': 278.00,
                                     'QARK': 1133.00,
                                     'REP': 1.55,
                                     'SRN': 2905.00,
                                     'SUSHI': 2.50,
                                     'TRX': 1.00,
                                     'UNI': 0.70,
                                     'USDC': 75.50,
                                     'USDT': 37.00,
                                     'XBX': 3285.00,
                                     'XIN': 5.00,
                                     'XLM': 0.005,
                                     'XRP': 0.10,
                                     'XTZ': 0.10,
                                     'ZEC': 0.004,
                                     'ZRX': 16.00}
                          }

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
DELAY_OF_EXPLORING_DATA = 5
DATA_LIMIT = 10


def getAvailableCryptoCurrenciesFromApi(url):
    headers = {'content-type': "application/json"}
    response = requests.request("GET", url, headers=headers)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        return None


def getOrdersBook(site, currencyPair):
    headers = {'content-type': "application/json"}
    response = requests.get(ORDER_BOOKS_URL[site] + currencyPair + ORDER_BOOKS_END_OF_URL[site],
                            headers=headers)
    if response.status_code in range(200, 299):
        tradeOffers = response.json()
        sellOffers = []
        buyOffers = []
        for asks in tradeOffers[ORDER_BOOKS_ASKS_OFFERS_NAMES[site]]:
            sellOffers.append([float(asks[ORDER_BOOKS_RATE_OFFERS_NAMES[site]]),
                               float(asks[ORDER_BOOKS_QUANTITY_OFFERS_NAMES[site]])])
        for bids in tradeOffers[ORDER_BOOKS_BIDS_OFFERS_NAMES[site]]:
            buyOffers.append([float(bids[ORDER_BOOKS_RATE_OFFERS_NAMES[site]]),
                              float(bids[ORDER_BOOKS_QUANTITY_OFFERS_NAMES[site]])])
        offers = {'bids': buyOffers, 'asks': sellOffers}
        return offers
    else:
        return None


def findCommonCryptoCurrenciesPairsFromTwoMarkets(site1, site2):
    market1Data = getAvailableCryptoCurrenciesFromApi(MARKETS_URL[site1])
    market2Data = getAvailableCryptoCurrenciesFromApi(MARKETS_URL[site2])
    marketList1 = getMarketList(site1, market1Data)
    marketList2 = getMarketList(site2, market2Data)
    commonCurrencyPairs = []
    for currency in marketList1:
        if currency in marketList2:
            commonCurrencyPairs.append(currency)
    return commonCurrencyPairs


def getMarketList(site, marketData):
    if type(marketData) is dict:
        return list(marketData[MARKETS_CURRENCIES_SYMBOL_NAMES[site]])
    else:
        return list(item[MARKETS_CURRENCIES_SYMBOL_NAMES[site]] for item in marketData)


def getWithdrawalFees(market):
    headers = {'content-type': "application/json"}
    response = requests.request("GET", MARKETS_WITHDRAWAL_FEES_URL[market], headers=headers)
    if response.status_code in range(200, 299):
        feesData = response.json()
        fees = {market: {}}
        for cryptocurrency in feesData:
            fees[market][cryptocurrency['symbol']] = float(cryptocurrency['txFee'])
        return fees
    else:
        return None


def calculateProfit

if __name__ == '__main__':
    #   print(getAvailableCryptoCurrenciesFromApi(MARKETS_URL['bitbay']))
    #   print(findCommonCryptoCurrenciesPairsFromTwoMarkets('bitbay', 'bittrex'))
    #   print(findCommonCryptoCurrenciesPairsFromTwoMarkets('bittrex', 'bitbay'))
    print(getWithdrawalFees('bittrex'))
