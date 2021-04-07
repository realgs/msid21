import requests
import time

OFFERS_LIMIT = 1
REFRESH_TIME = 5
BASE_CURRENCY = "USD"
CRYPTO_CURRENCIES = ["BTC", "LTC", "XRP"]
ACTIONS = ['bids', 'asks']
APIS = [
    {
        'stockName': 'BITBAY',
        'url': "https://bitbay.net/API/Public/",
        'takerFee': 0.0031, # 0.31% z transakcji
        'transferFee': {  # to nie procent, tylko kwota
            "BTC": 0.0005,
            "LTC": 0.001,
            "XRP": 0.1
        }
    },
    {
        'stockName': 'BITSTAMP',
        'url': "https://www.bitstamp.net/api/v2/",
        'takerFee': 0.0022,  # 0.22% z transakcji - < 200,000$
        'transferFee': {  # to nie procent, tylko kwota
            "BTC": 0.0005,
            "LTC": 0.001,
            "XRP": 0.02
        }
    }
]


def getApiResponse(url):
    response = requests.get(url)
    if response.status_code in range(200, 299):
        return response.json()
    else:
        print(response.reason)
        return None


def getOffers(base, crypto, stockName):
    if stockName == APIS[0]["stockName"]:  # bitbay
        apiResponse = getApiResponse(f'{APIS[0]["url"]}{crypto}{base}/orderbook.json')
        if apiResponse is not None:
            return {'bids': apiResponse['bids'][:OFFERS_LIMIT], 'asks': apiResponse['asks'][:OFFERS_LIMIT]}

    elif stockName == APIS[1]["stockName"]:  # bitstamp
        apiResponse = getApiResponse(f'{APIS[1]["url"]}order_book/{crypto.lower()}{base.lower()}')
        if apiResponse is not None:
            return {'bids': list(map(lambda x: [float(x[0]), float(x[1])], apiResponse['bids'][:OFFERS_LIMIT])),
                    'asks': list(map(lambda x: [float(x[0]), float(x[1])], apiResponse['asks'][:OFFERS_LIMIT]))}
    else:
        return None


# exc 1 a and b
def buyOrSellDifference(crypto, stockName1, stockName2, action):
    apiOffer1 = getOffers(BASE_CURRENCY, crypto, stockName1)
    apiOffer2 = getOffers(BASE_CURRENCY, crypto, stockName2)
    if apiOffer1 and apiOffer2:
        return ((apiOffer1[action][0][0] - apiOffer2[action][0][0]) / apiOffer1[action][0][0]) * 100
    else:
        return None


# exc 1 c
def arbitrageValue(crypto, apiName1, apiName2):
    apiOffer1 = getOffers(BASE_CURRENCY, crypto, apiName1)
    apiOffer2 = getOffers(BASE_CURRENCY, crypto, apiName2)
    if apiOffer1 and apiOffer2:
        return ((apiOffer2['bids'][0][0] - apiOffer1['asks'][0][0]) / apiOffer2['bids'][0][0]) * 100
    else:
        return None


# exc 1 - whole
def exc1(crypto, stockName1, stockName2):
    while True:
        print(f'{stockName1} to {stockName2}')
        print(f'Buy difference: {buyOrSellDifference(crypto, stockName1, stockName2, ACTIONS[0])}% for {crypto}')  # bids
        print(f'Sell difference: {buyOrSellDifference(crypto, stockName1, stockName2, ACTIONS[1])}% for {crypto} \n')  # asks

        print(f'Purchase at {stockName1} and put up for sale at {stockName2}')  # stock1 - asks, stock2 - bids
        print(f'Arbitrage: {arbitrageValue(crypto, stockName1, stockName2)}% for {crypto} \n')

        print(f'Purchase at {stockName2} and put up for sale at {stockName1}')  # stock2 - asks, stock1 - bids
        print(f'Arbitrage: {arbitrageValue(crypto, stockName2, stockName1)}% for {crypto}\n')

        time.sleep(REFRESH_TIME)


if __name__ == "__main__":
    # zadanie 1 results
    exc1(CRYPTO_CURRENCIES[0], APIS[0]["stockName"], APIS[1]["stockName"])
