import requests

BITTREX_MARKET_URL = 'https://api.bittrex.com/v3/markets/'
BITBAY_MARKET_URL = 'https://api.bitbay.net/rest/trading/ticker'

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

if __name__ == '__main__':
    print(getCommonMarket(getBitbayMarket(), getBittrexMarket()))
