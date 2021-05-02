import requests

BITTREX_MARKET_URL = 'https://api.bittrex.com/v3/markets/'
BITBAY_MARKET_URL = 'https://api.bitbay.net/rest/trading/ticker'
DEFAULT_SEARCHING_DEPTH = 5

BITTREX_ORDER_URL = 'https://api.bittrex.com/v3/markets/'
BITTREX_ORDER_URL_2 = '/orderbook'
BITTREX_FEES = {
    'taker': 0.0035,
    'transfer': { 'BTC': 0.0005, 'ETH': 0.006 , 'USD': 0 }
}
BITBAY_ORDER_URL = 'https://bitbay.net/API/Public/'
BITBAY_ORDER_URL_2 = '/orderbook.json'
BITBAY_FEES = {
    'taker': 0.0042,
    'transfer': { 'BTC': 0.0005, 'ETH': 0.01 , 'USD': 3 }
}

def getBittrexMarket():
    result = []
    bittrexDownload = requests.get(BITTREX_MARKET_URL)

    if (bittrexDownload.status_code == 200):
        bittrexJson = bittrexDownload.json()

        for element in range(0, len(bittrexJson)):
            result.append(bittrexJson[element]['symbol'])

    return result

def getBitbayMarket():
    result = []
    bitbayDownload = requests.get(BITBAY_MARKET_URL)

    if (bitbayDownload.status_code == 200):
        bitbayJson = bitbayDownload.json()
        bitbayItems = bitbayJson['items']
        bitbayKeys = bitbayItems.keys()

        for element in bitbayKeys:
            result.append(element)

    return result

def getCommonMarket(market1, market2):
    result = []
    for element in market1:
        if (market2.__contains__(element)):
            result.append(element)

    result.sort()

    return result

#-----------------------------------------------------------------------------------------------------------------------

def getOffers(resource, depth=DEFAULT_SEARCHING_DEPTH):
    result = {'resource': resource, 'bittrex': {}, 'bitbay': {}}


    result['bittrex']['bidPrice'] = []
    result['bittrex']['bidAmmount'] = []
    result['bittrex']['askPrice'] = []
    result['bittrex']['askAmmount'] = []

    bittrexDownload = requests.get(BITTREX_ORDER_URL + resource + BITTREX_ORDER_URL_2)
    if (bittrexDownload.status_code == 200):

        bittrexJson = bittrexDownload.json()

        for i in range(depth):
            result['bittrex']['bidPrice'].append(bittrexJson['bid'][i]['rate'])
        for i in range(depth):
            result['bittrex']['bidAmmount'].append(bittrexJson['bid'][i]['quantity'])
        for i in range(depth):
            result['bittrex']['askPrice'].append(bittrexJson['ask'][i]['rate'])
        for i in range(depth):
            result['bittrex']['askAmmount'].append(bittrexJson['ask'][i]['quantity'])



    result['bitbay']['bidPrice'] = []
    result['bitbay']['bidAmmount'] = []
    result['bitbay']['askPrice'] = []
    result['bitbay']['askAmmount'] = []

    bitbayDownload = requests.get(BITBAY_ORDER_URL + resource.replace('-', '') + BITBAY_ORDER_URL_2)
    if (bitbayDownload.status_code == 200):

        bitbayJson = bitbayDownload.json()

        for i in range(depth):
            result['bitbay']['bidPrice'].append(bitbayJson['bids'][i][0])
        for i in range(depth):
            result['bitbay']['bidAmmount'].append(bitbayJson['bids'][i][1])
        for i in range(depth):
            result['bitbay']['askPrice'].append(bitbayJson['asks'][i][0])
        for i in range(depth):
            result['bitbay']['askAmmount'].append(bitbayJson['asks'][i][1])


    return result


if __name__ == '__main__':
    commonMarket = (getCommonMarket(getBitbayMarket(), getBittrexMarket()))
    data = getOffers(commonMarket[0])
    print(data['bitbay']['bidPrice'])
