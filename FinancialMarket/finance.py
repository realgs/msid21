import requests
import time

BitBayApiURL = "https://bitbay.net/API/Public/"
offersLimit = 5
refreshTime = 5  # 5 seconds
BTCUSD = ('BTC', 'USD')
LTCUSD = ('LTC', 'USD')
DASHUSD = ('DASH', 'USD')


# zadanie 1
def getApiResponse(url):
    response = requests.get(url)
    if response.status_code >= 200 or response.status_code <= 299:
        return response.json()
    else:
        print(response.reason)
        return None


def getOffersFromBitBay(marketSymbols):
    apiResponse = getApiResponse(f'{BitBayApiURL}{marketSymbols[0]}{marketSymbols[1]}/orderbook.json')
    if apiResponse is not None:
        return {'bids': apiResponse['bids'][:offersLimit], 'asks': apiResponse['asks'][:offersLimit]}
    else:
        return None


def printOffersFromBitBay(marketSymbols):
    offers = getOffersFromBitBay(marketSymbols)
    if offers is not None:
        bids = offers['bids']
        asks = offers['asks']

        print(f'Buy: {marketSymbols[0]} - {marketSymbols[1]}')
        for offer in bids:
            print(f'{offer[1]} {marketSymbols[0]} for {offer[0] * offer[1]} {marketSymbols[1]}')

        print()

        print(f'Sale: {marketSymbols[0]} - {marketSymbols[1]}')
        for offer in asks:
            print(f'{offer[1]} {marketSymbols[0]} for {offer[0] * offer[1]} {marketSymbols[1]}')
    else:
        print("Couldn't get data about currencies")


# zadanie 2
def calculateProfitabilityFromBitBay(marketSymbols):
    while True:
        offers = getOffersFromBitBay(marketSymbols)
        if offers is not None:
            bids = offers['bids']
            asks = offers['asks']

            buyOfferPrice = bids[0][0]  # takes the best option
            sellOfferPrice = asks[0][0]  # takes the best option

            ratio = (1 - (sellOfferPrice - buyOfferPrice) / buyOfferPrice)
            print(f'Profitability for {marketSymbols[0]}: {ratio * 100} %')
        else:
            print("Couldn't get data about currencies")

        time.sleep(refreshTime)


if __name__ == "__main__":
    # zadanie 1 results
    printOffersFromBitBay(BTCUSD)
    print()
    printOffersFromBitBay(LTCUSD)
    print()
    printOffersFromBitBay(DASHUSD)
    print()

    # zadanie 2 results
    # calculateProfitabilityFromBitBay(BTCUSD)  # endless loop
    calculateProfitabilityFromBitBay(LTCUSD)  # endless loop
    # calculateProfitabilityFromBitBay(DASHUSD)  # endless loop
