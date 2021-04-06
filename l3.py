import requests

TRADE_MARKETS = ['bitbay', 'bittrex']
MARKETS_URL = ['https://bitbay.net/API/Public/', 'https://api.bittrex.com/v3/markets']

def getDataFromApi(url):
    response = requests.get(url)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        return None

def getSellBuyOffers(exchangeMarket, jsonObjectIndex, limit):
    


