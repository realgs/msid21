import requests
import time

BitBayApiURL = "https://bitbay.net/API/Public/"
offersLimit = 5
refreshTime = 5
baseCurrency = "USD"
cryptoCurrencies = ["BTC", "LTC", "DASH"]


# zadanie 1
def getApiResponse(url):
    response = requests.get(url)
    if response.status_code >= 200 or response.status_code <= 299:
        return response.json()
    else:
        print(response.reason)
        return None


def getOffersFromBitBay(base, crypto):
    apiResponse = getApiResponse(f'{BitBayApiURL}{crypto}{base}/orderbook.json')
    if apiResponse is not None:
        return {'bids': apiResponse['bids'][:offersLimit], 'asks': apiResponse['asks'][:offersLimit]}
    else:
        return None


def printOffersFromBitBay(base, crypto):
    offers = getOffersFromBitBay(base, crypto)
    if offers is not None:
        bids = offers['bids']
        asks = offers['asks']

        print(f'Buy: {base} - {crypto}')
        for offer in bids:
            print(f'{offer[1]} {base} for {offer[0] * offer[1]} {crypto}')

        print(f'Sale: {base} - {crypto}')
        for offer in asks:
            print(f'{offer[1]} {base} for {offer[0] * offer[1]} {crypto}')
        print()
    else:
        print("Couldn't get data about currencies\n")


# zadanie 2
def calculateSpreadFromBitBay(base, crypto):
    while True:
        offers = getOffersFromBitBay(base, crypto)
        if offers is not None:
            bids = offers['bids']
            asks = offers['asks']

            buyOfferPrice = bids[0][0]  # takes the best option
            sellOfferPrice = asks[0][0]  # takes the best option

            ratio = (1 - (sellOfferPrice - buyOfferPrice) / buyOfferPrice)
            print(f'Profitability for {base}: {ratio * 100} %')
        else:
            print("Couldn't get data about currencies\n")

        time.sleep(refreshTime)


if __name__ == "__main__":
    # zadanie 1 results
    for cryptoCurrency in cryptoCurrencies:
        printOffersFromBitBay(baseCurrency, cryptoCurrency)

    # zadanie 2 results
    calculateSpreadFromBitBay(baseCurrency, cryptoCurrencies[1])  # example - endless loop

