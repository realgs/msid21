import requests

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

# chosen markets for ex. 2
MARKETS = ['BTC-AMP', 'USDT-ETC', 'ETH-ETC']


def getMarkets(apiName):
    offerList = requests.get(API[apiName]["URL"].format(API[apiName]['MARKETS']))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getMarketsLists():
    poloniexMarkets = getMarkets('POLONIEX')
    bittrexMarkets = getMarkets('BITTREX')
    bittrexCurrencyList, poloniexCurrencyList = [], []
    for pair in bittrexMarkets['result']:
        bittrexCurrencyList.append(pair['MarketName'])
    for pair in poloniexMarkets.keys():
        pair = pair.replace('_', '-')
        poloniexCurrencyList.append(pair)
    return poloniexCurrencyList, bittrexCurrencyList


def getCommonMarkets():
    polList, bitList = getMarketsLists()
    res = list(set(polList) & set(bitList))
    res.sort()
    return res


def getTxList(apiName):
    offerList = requests.get(API[apiName]["URL"].format(API[apiName]['TXFEES']))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def getTxFeePoloniex(currency):
    feesList = getTxList('POLONIEX')
    return feesList[currency.split('-')[0]]['txFee']


def getTxFeeBittrex(currency):
    fee = 0
    feesList = getTxList('BITTREX')
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


def getOffers(currency, apiName):
    offerList = requests.get(API[apiName]["URL"].format(API[apiName]['ORDERBOOK'].format(currency)))
    if offerList.status_code == 200:
        return offerList.json()
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def downloadData(currency, apiName):
    if apiName == 'BITTREX':
        offersData = getOffers(currency, apiName)
        bids = offersData['result'][API[apiName]['BIDS']]
        asks = offersData['result'][API[apiName]['ASKS']]
    else:
        currency = currency.replace('-', '_')
        offersData = getOffers(currency, apiName)
        bids = offersData[API[apiName]['BIDS']]
        asks = offersData[API[apiName]['ASKS']]
    return [bids, asks]


def calculateDifference(first, second):
    difference = (1 - (first - second) / second) * 100
    return difference


def calculateCost(quantity, rate, apiName, txFee):
    return float(rate) * (float(quantity) * (1 + float(API[apiName]['TAKER'])) + float(txFee))


def calculateProfit(quantity, rate, apiName):
    return float(rate) * float(quantity) * (1 - float(API[apiName]['TAKER']))


def calculateArbitrage(currency, api1, api2):
    [bids_api1, _] = downloadData(currency, api1)
    [_, asks_api2] = downloadData(currency, api2)

    i, j, askVolume, bidVolume, cost, profit, temp = 0, 0, 0, 0, 0, 0, 0
    if not asks_api2 or not bids_api1:
        return 0, currency
    else:
        for ask in asks_api2:
            if float(ask[API[api2]['RATE']]) < float(bids_api1[0][API[api1]['RATE']]):
                askVolume += float(ask[API[api2]['QUANTITY']])
                i += 1
        for bid in bids_api1:
            if float(bid[API[api1]['RATE']]) > float(asks_api2[i - 1][API[api2]['RATE']]):
                bidVolume += float(bid[API[api1]['QUANTITY']])
                j += 1
        finalAsks = asks_api2[:i]
        finalBids = bids_api1[:j]

        volumeDifference = float(abs(askVolume - bidVolume))
        finalAsks.sort(key=lambda x: abs(float(x[API[api2]['QUANTITY']]) - volumeDifference))
        while len(finalAsks) > 0 and askVolume - float(finalAsks[0][API[api2]['QUANTITY']]) > bidVolume:
            askVolume -= float(finalAsks[0][API[api2]['QUANTITY']])
            finalAsks = finalAsks[1:]

        finalBids.sort(key=lambda x: abs(x[API[api1]['QUANTITY']] - volumeDifference))
        while askVolume < bidVolume:
            bidVolume -= finalBids[0][API[api1]['QUANTITY']]
            finalBids = finalBids[1:]

        leftoverVolume = askVolume - bidVolume
        if not finalAsks or not finalBids:
            return 0, currency
        else:
            txFeeAsk = getTxFee(api2, currency)
            for ask in finalAsks:
                cost += calculateCost(ask[API[api2]['QUANTITY']], ask[API[api2]['RATE']], api2, txFeeAsk)
            for bid in finalBids:
                profit += calculateProfit(bid[API[api1]['QUANTITY']], bid[API[api1]['RATE']], api1)

            leftoverCost = leftoverVolume * float(finalBids[0][API[api1]['RATE']])
            baseIncome = profit + leftoverCost - cost
            if baseIncome < 0:
                return 0, currency
            else:
                return baseIncome, calculateDifference(cost, profit + leftoverCost), currency


def rankArbitrage(api1, api2, currencies):
    currenciesList = []
    for currency in currencies:
        currenciesList.append(calculateArbitrage(currency, api1, api2))
    currenciesList.sort(key=lambda x: x[0], reverse=True)
    print(f'Arbitrage ranking from {api2} to {api1}:')
    for result in currenciesList:
        if len(result) == 2:
            print(f"{result[1]} - arbitrage impossible!")
        else:
            print(f"{result[2]} - arbitrage possible! Profit: {result[0]} - {result[1]}%")


if __name__ == '__main__':
    # ex. 1
    commonMarkets = getCommonMarkets()
    print(commonMarkets)
    # ex. 2
    rankArbitrage('POLONIEX', 'BITTREX', MARKETS)
    rankArbitrage('BITTREX', 'POLONIEX', MARKETS)
    # ex. 3
    rankArbitrage('BITTREX', 'POLONIEX', commonMarkets)
    rankArbitrage('POLONIEX', 'BITTREX', commonMarkets)
