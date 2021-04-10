import requests
import time

SINGLE_OFFER = 1
OFFERS_AMOUNT = 100
REFRESH_TIME = 5
BASE_CURRENCY = "USD"
CRYPTO_CURRENCIES = ["BTC", "ETH", "XRP"]
ACTIONS = ['bids', 'asks']
APIS = [
    {
        'stockName': 'BITBAY',
        'url': "https://bitbay.net/API/Public/",
        'takerFee': 0.0031,  # 0.31% z transakcji
        'transferFee': {  # to nie procent, tylko kwota
            "BTC": 0.0005,
            "LTC": 0.001,
            "XRP": 0.1,
            "ETH": 0.01
        }
    },
    {
        'stockName': 'BITSTAMP',
        'url': "https://www.bitstamp.net/api/v2/",
        'takerFee': 0.0022,  # 0.22% z transakcji - < 200,000$
        'transferFee': {  # to nie procent, tylko kwota
            "BTC": 0.0005,
            "LTC": 0.001,
            "XRP": 0.02,
            "ETH": 0.03
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


def getOffers(base, crypto, stockName, amountOfOffers=SINGLE_OFFER):
    if stockName == APIS[0]["stockName"]:  # bitbay
        apiResponse = getApiResponse(f'{APIS[0]["url"]}{crypto}{base}/orderbook.json')
        if apiResponse is not None:
            return {'bids': apiResponse['bids'][:min(amountOfOffers, len(apiResponse['bids']))],
                    'asks': apiResponse['asks'][:min(amountOfOffers, len(apiResponse['asks']))]}

    elif stockName == APIS[1]["stockName"]:  # bitstamp
        apiResponse = getApiResponse(f'{APIS[1]["url"]}order_book/{crypto.lower()}{base.lower()}')
        if apiResponse is not None:
            return {'bids': list(map(lambda x: [float(x[0]), float(x[1])],
                                     apiResponse['bids'][:min(amountOfOffers, len(apiResponse['bids']))])),
                    'asks': list(map(lambda x: [float(x[0]), float(x[1])],
                                     apiResponse['asks'][:min(amountOfOffers, len(apiResponse['asks']))]))}

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
def idealArbitrageValue(crypto, stockName1, stockName2):
    apiOffer1 = getOffers(BASE_CURRENCY, crypto, stockName1)
    apiOffer2 = getOffers(BASE_CURRENCY, crypto, stockName2)
    if apiOffer1 and apiOffer2:
        return ((apiOffer2['bids'][0][0] - apiOffer1['asks'][0][0]) / apiOffer2['bids'][0][0]) * 100
    else:
        return None


# exercise 2 methods
# zwraca tablice [koszt oferty, ilość] - koszt oferty to cena * wolumen
def offersCostAndVolume(stockOffers, action):
    costAndVolume = []
    for offer in stockOffers[action]:
        cost = float(offer[0]) * float(offer[1])
        costAndVolume.append([cost, float(offer[1])])
    return costAndVolume


# dolicza taker fee jakie trzeba będzie zapłacić
def addTakerFee(costsAndVolumes, stockName):
    costAndVolumeWithFee = []
    fee = APIS[0]["takerFee"] if stockName == APIS[0]["stockName"] else APIS[1]["takerFee"]
    for offer in costsAndVolumes:
        newCost = (offer[0] * (1 + fee))
        costAndVolumeWithFee.append([newCost, float(offer[1])])
    return costAndVolumeWithFee


# dolicza transfer fee do asks
def addTransferFee(costsAndVolumes, stockName, crypto):
    costAndVolumeWithFee = []
    fee = APIS[0]["transferFee"][crypto] if stockName == APIS[0]["stockName"] else APIS[1]["transferFee"][crypto]
    for offer in costsAndVolumes:
        quantity = offer[1] - fee
        costAndVolumeWithFee.append([offer[0], quantity])
    return costAndVolumeWithFee


# analizuje arbitraż dla "przygotowanych danych"
def calculateArbitrage(toPurchase, toSell):
    spentMoney = 0
    earnedMoney = 0
    for purchase in toPurchase:
        for sell in toSell:
            buyExchangeRatio = purchase[0] / purchase[1] if purchase[1] != 0 else 0
            sellExchangeRatio = sell[0] / sell[1] if sell[1] != 0 else 0
            if buyExchangeRatio < sellExchangeRatio:
                stocksBought = min(purchase[1], sell[1])
                spentMoney += buyExchangeRatio * stocksBought
                earnedMoney += sellExchangeRatio * stocksBought
                purchase[0] -= buyExchangeRatio * stocksBought
                purchase[1] -= stocksBought
                sell[0] -= sellExchangeRatio * stocksBought
                sell[1] -= stocksBought
                if sell[1] == 0:
                    toSell.remove(sell)
                if purchase[1] == 0:
                    toPurchase.remove(purchase)
                    break
    profit = earnedMoney - spentMoney
    percentage_earned = profit / spentMoney * 100 if spentMoney != 0 else 0
    return spentMoney, percentage_earned, profit


# exc 2
def arbitrageValue(crypto, stockName1, stockName2):  # dla mnie, niech apiName1 bedzie BitBay, a apiName2 BitStamp
    stockOffer1 = getOffers(BASE_CURRENCY, crypto, stockName1, OFFERS_AMOUNT)  # oferty z bitbaya
    stockOffer2 = getOffers(BASE_CURRENCY, crypto, stockName2, OFFERS_AMOUNT)  # oferty z bitstampa

    stock1AsksCostsAndVolume = offersCostAndVolume(stockOffer1, 'asks')  # oferty jakie moge skupić z bitbaya - koszty
    stock2BidsCostsAndVolume = offersCostAndVolume(stockOffer2, 'bids')  # ofery jakie moge sprzedać na bitstampie - koszty

    stock1AsksCostsAndVolumeWithTakerFee = addTakerFee(stock1AsksCostsAndVolume, stockName1)  # to samo co wyżej tylko po dodaniu taker fee
    stock2BidsCostsAndVolumeWithTakerFee = addTakerFee(stock2BidsCostsAndVolume, stockName2)  # to samo co wyżej tylko po dodaniu taker fee

    stock1AsksCostsAndVolumeWithTakerAndTransferFee = addTransferFee(stock1AsksCostsAndVolumeWithTakerFee, stockName1, crypto)

    result = calculateArbitrage(stock1AsksCostsAndVolumeWithTakerAndTransferFee, stock2BidsCostsAndVolumeWithTakerFee)
    return result


def exc1And2(crypto, stockName1, stockName2):
    while True:
        # exc 1 - whole
        print(f'{stockName1} to {stockName2} buy difference: {buyOrSellDifference(crypto, stockName1, stockName2, ACTIONS[0])}% for {crypto}')  # bids
        print(f'{stockName1} to {stockName2} sell difference: {buyOrSellDifference(crypto, stockName1, stockName2, ACTIONS[1])}% for {crypto} \n')  # asks

        print(f'Purchase at {stockName1} and put up for sale at {stockName2}')  # stock1 - asks, stock2 - bids
        print(f'Ideal arbitrage: {idealArbitrageValue(crypto, stockName1, stockName2)}% for {crypto} \n')

        print(f'Purchase at {stockName2} and put up for sale at {stockName1}')  # stock2 - asks, stock1 - bids
        print(f'Ideal arbitrage: {idealArbitrageValue(crypto, stockName2, stockName1)}% for {crypto}\n')

        # exc 2 - whole
        stock1ToStock2 = arbitrageValue(crypto, stockName1, stockName2)
        print(f'Purchase at {stockName1} and put up for sale at {stockName2}')  # stock1 - asks, stock2 - bids
        print(f'Arbitrage: {round(stock1ToStock2[1], 2)}%, to earn: {round(stock1ToStock2[2], 2)} {BASE_CURRENCY}, {round(stock1ToStock2[0],2)} {BASE_CURRENCY} available for arbitrage\n')

        stock2ToStock1 = arbitrageValue(crypto, stockName2, stockName1)
        print(f'Purchase at {stockName2} and put up for sale at {stockName1}')  # stock1 - asks, stock2 - bids
        print(f'Arbitrage: {round(stock2ToStock1[1], 2)}%, to earn: {round(stock2ToStock1[2], 2)} {BASE_CURRENCY}, {round(stock2ToStock1[0], 2)} {BASE_CURRENCY} available for arbitrage\n')
        print("#######################################################################################################")
        time.sleep(REFRESH_TIME)


if __name__ == "__main__":
    exc1And2(CRYPTO_CURRENCIES[1], APIS[0]["stockName"], APIS[1]["stockName"])
