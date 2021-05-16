import requests
import time

# api data
API = {
    'BITTREX': {
        "URL": 'https://api.bittrex.com/api/v1.1/public/{}',
        "MARKETS": 'getmarkets',
        "ORDERBOOK": 'getorderbook?market={}&type=both',
        "TXFEES": 'getcurrencies',
        "ASKS": 'sell',
        "BIDS": 'buy',
        "RATE": 'Rate',
        "QUANTITY": 'Quantity',
        "TAKER": 0.0075,
    },

    'POLONIEX': {
        "URL": 'https://poloniex.com/public?command={}',
        "MARKETS": 'returnTicker',
        "ORDERBOOK": 'returnOrderBook&currencyPair={}',
        "TXFEES": 'returnCurrencies',
        "ASKS": 'asks',
        "BIDS": 'bids',
        "RATE": 0,
        "QUANTITY": 1,
        "TAKER": 0.00125,
    }
}

# general data
CURRENCIES = ['BTC-DOGE', 'USDT-ETH', 'BTC-CVT']  # <- zad 2
# BASE_CURRENCY = 'USD'
DELAY = 5


def getBtrx():
    offerList = requests.get('https://api.bittrex.com/api/v1.1/public/getmarkets')
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getPol():
    offerList = requests.get('https://poloniex.com/public?command=returnTicker')
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getList():
    polonix = getPol()
    bittrex = getBtrx()
    polList = polonix.keys()
    bitList = bittrex['result']
    bitCurrencyList, polCurrencyList = [], []
    for pair in bitList:
        bitCurrencyList.append(pair['MarketName'])
    for pair in polList:
        pair = pair.replace('_', '-')
        polCurrencyList.append(pair)
    print(polCurrencyList)
    print(bitCurrencyList)
    return polCurrencyList, bitCurrencyList


def getCommonCurrencies():
    polList, bitList = getList()
    res = list(set(polList) & set(bitList))
    res.sort()
    print(res)
    return res


def getTxListBittrex():
    offerList = requests.get('https://api.bittrex.com/api/v1.1/public/getcurrencies')
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getTxListPoloniex():
    offerList = requests.get('https://poloniex.com/public?command=returnCurrencies')
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getTxFeePoloniex(currency):
    feesList = getTxListPoloniex()
    return feesList[currency.split('-')[0]]['txFee']


def getTxFeeBittrex(currency):
    fee = 0
    feesList = getTxListBittrex()
    for curr in feesList['result']:
        if curr['Currency'] == currency:
            fee = curr['TxFee']
    return fee


def getTxFee(apiName, currency):
    if apiName == 'BITTREX':
        return getTxFeeBittrex(currency)
    if apiName == 'POLONIEX':
        return getTxFeePoloniex(currency)
    else:
        return None


# zad 2 i 3
def getOffers(currency, apiName):
    offerList = requests.get(API[apiName]["URL"].format(API[apiName]['ORDERBOOK'].format(currency)))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def downloadData(currency, api):
    if api == 'BITTREX':
        offersData = getOffers(currency, api)
        bids = offersData['result'][API[api]['BIDS']]
        asks = offersData['result'][API[api]['ASKS']]
    else:
        currency = currency.replace('-', '_')
        offersData = getOffers(currency, api)
        bids = offersData[API[api]['BIDS']]
        asks = offersData[API[api]['ASKS']]
    return [bids, asks]


def calculateDifference(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def getBestBid(currency, apiName):
    [bids, asks] = downloadData(currency, apiName)
    return [bids, asks][0][0][API[apiName]['RATE']]


def getBestAsk(currency, apiName):
    [bids, asks] = downloadData(currency, apiName)
    return [bids, asks][1][0][API[apiName]['RATE']]


def calculateDifferenceBetweenApis(currency, api1, api2):
    bid_api1 = getBestBid(currency, api1)
    ask_api2 = getBestAsk(currency, api2)
    print(f'Best offers: \t\t\tbid: {api1} {bid_api1}\t\t\t\t\task: {api2} {ask_api2}')
    return calculateDifference(float(ask_api2), float(bid_api1))


# zad 1c
def printDifferenceApis(api1, api2):
    print("Apis:")
    for currency in CURRENCIES:
        difference = calculateDifferenceBetweenApis(currency, api1, api2)
        print(f'Currency: {currency}\t\tDifference: {difference}%')


# zad 2
def calculateCost(quantity, rate, apiName, currency):
    return float(rate) * (float(quantity) * (1 + float(API[apiName]['TAKER'])) + float(getTxFee(apiName, currency)))


def calculateProfit(quantity, rate, apiName):
    return float(rate) * float(quantity) * (1 - float(API[apiName]['TAKER']))


def printArbitrageImpossible(currency, api1, api2):
    print(f"Arbitrage for {currency} impossible!")
    print(f'Buying from {api2} and selling to {api1}')


def calculateArbitrage(currency, api1, api2):
    [bids_api1, _] = downloadData(currency, api1)
    [_, asks_api2] = downloadData(currency, api2)

    i, j, askQuantity, bidQuantity, cost, profit = 0, 0, 0, 0, 0, 0
    for ask in asks_api2:
        if float(ask[API[api2]['RATE']]) < float(bids_api1[0][API[api1]['RATE']]):
            askQuantity += float(ask[API[api2]['QUANTITY']])
            i += 1
    for bid in bids_api1:
        if float(bid[API[api1]['RATE']]) > float(asks_api2[i - 1][API[api2]['RATE']]):
            bidQuantity += float(bid[API[api1]['QUANTITY']])
            j += 1
    finalAsks = asks_api2[:i]
    finalBids = bids_api1[:j]
    print(finalAsks)
    print(finalBids)
    print(f'as: {askQuantity}, bi: {bidQuantity}')
    while askQuantity < bidQuantity:
        finalBids.sort(key=lambda x: x[API[api1]['QUANTITY']])
        bidQuantity -= finalBids[0][API[api1]['QUANTITY']]
        finalBids = finalBids[1:]

    finalAsks.sort(key=lambda x: x[API[api2]['QUANTITY']])
    while askQuantity > bidQuantity:
        askQuantity -= finalAsks[0][API[api2]['QUANTITY']]
        finalAsks = finalAsks[1:]
    print(f'as: {askQuantity}, bi: {bidQuantity}')


    leftoverQuantity = askQuantity - bidQuantity
    if not finalAsks or not finalBids:
        printArbitrageImpossible(currency, api1, api2)
    else:
        print(asks_api2)
        print(finalAsks)
        print(bids_api1)
        print(finalBids)
        print(f'left: {leftoverQuantity}, ask: {askQuantity}, bid: {bidQuantity}')
        for ask in finalAsks:
            cost += calculateCost(ask[API[api2]['QUANTITY']], ask[API[api2]['RATE']], api2, currency)

        for bid in finalBids:
            profit += calculateProfit(bid[API[api1]['QUANTITY']], bid[API[api1]['RATE']], api1)

        baseIncome = profit - cost
        if baseIncome < 0:
            print(baseIncome)
            printArbitrageImpossible(currency, api1, api2)
        else:
            print("Arbitrage was possible!")
            print(f'Buying from {api2} and selling to {api1}')
            print(f'Total profit for {currency}:\t{baseIncome}USD')
            print(f'Profit in percentage: {calculateDifference(cost, profit)}')
            print(f'Quantity of the currency: BOUGHT: {askQuantity}, SOLD: {bidQuantity}, LEFT: {leftoverQuantity}')


def getCurrencies():
    offerList = requests.get('https://api.cryptomkt.com/v1/market')
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def printData(api):
    offersData = getCurrencies()
    for offer in offersData:
        print(offer)
    else:
        print(f'Cannot load market data from {api["name"]}!')
        return None


def calculateChosenCurrencies(api1, api2):
    for currency in CURRENCIES:
        calculateArbitrage(currency, api1, api2)


def calculateCommonCurrencies(api1, api2):
    commonCurrecies = getCommonCurrencies()
    for currency in commonCurrecies:
        calculateArbitrage(currency, api1, api2)


def main():
    #getCommonCurrencies()

    #print(downloadData('BTC-AAVE', 'BITTREX'))
    #print(downloadData('BTC-AAVE', 'POLONIEX'))
    # printDifferenceApis('BITTREX', 'POLONIEX')
    # calculateArbitrage('BTC-AAVE', 'BITTREX', 'POLONIEX')


    #calculateChosenCurrencies('POLONIEX', 'BITTREX')
    #calculateChosenCurrencies('BITTREX', 'POLONIEX')
    calculateCommonCurrencies('BITTREX', 'POLONIEX')


if __name__ == '__main__':
    main()
