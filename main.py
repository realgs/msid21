import requests
from time import sleep
from typing import Tuple, List


def bitbayUrlFormat(apiUrl: str, marketSymbol: Tuple[str, str], endPoint: str):
    return f'{apiUrl}/{marketSymbol[0]}{marketSymbol[1]}/{endPoint}'


def bittrexUrlFormat(apiUrl: str, marketSymbol: Tuple[str, str], endPoint: str):
    return f'{apiUrl}/{marketSymbol[0]}-{marketSymbol[1]}/{endPoint}'


APIS: List[dict] = [
    {
        'title': 'bitbay',
        'url': 'https://bitbay.net/API/Public',
        'endPoint': 'orderbook.json',
        'urlFormatFunction': bitbayUrlFormat,
        'takerFee': 0.001,
        'transferFee': {
            'BAT': 61.0,
            'BTC': 0.0005,
            'ETH': 0.01,
            'XLM': 0.005
        }
    },
    {
        'title': 'bittrex',
        'url': 'https://api.bittrex.com/v3/markets',
        'endPoint': 'orderbook',
        'urlFormatFunction': bittrexUrlFormat,
        'takerFee': 0.0075,
        'transferFee': {
            'BAT': 50.0,
            'BTC': 0.00015,
            'ETH': 0.0017,
            'XLM': 0.005
        }
    }
]


def fetchData(url: str):
    try:
        response = requests.get(url)
        if response.status_code in range(200, 299):
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print("Error occured while connecting to the API.")
    except requests.exceptions.Timeout:
        print("System timeout. Could not connect to the API.")

    return None


def getOffers(marketSymbol: Tuple[str, str], numberOfOffers: int, apiObject: dict):
    if numberOfOffers <= 0: raise Exception("Number of offers should be positive.")
    tradeOffers = fetchData(apiObject['urlFormatFunction'](apiObject['url'], marketSymbol, apiObject['endPoint']))
    if tradeOffers:
        for key, value in tradeOffers.items():
            value = value[:numberOfOffers]
            value = list(map(lambda offer: {
                'quantity': float(offer["quantity"] if isinstance(offer, dict) else offer[1]),
                'rate': float(offer["rate"] if isinstance(offer, dict) else offer[0])
            }, value))
            tradeOffers[key] = sorted(value, key=lambda val: val["rate"])

        bids = tradeOffers["bids" if "bids" in tradeOffers else "bid"]
        asks = tradeOffers["asks" if "asks" in tradeOffers else "ask"]
        return {"bids": bids, "asks": asks}
    else:
        raise Exception(f'Unable to load a market for {marketSymbol[0]}-{marketSymbol[1]}.')


def displayOffers(marketSymbol: Tuple[str, str], offers: List[dict[str, float]]):
    for offer in offers:
        print(f'Price (' + '{:.4f}'.format(offer["quantity"]) + f' {marketSymbol[0]}):',
              '{:.4f}'.format(offer["quantity"] * offer["rate"]) + f' {marketSymbol[1]}')
        print(f'Price (1 {marketSymbol[0]}):', f'{offer["rate"]} {marketSymbol[1]} \n')


def findPriceDifferences(offers1: List[dict[str, float]], offers2: List[dict[str, float]]):
    offersSize1 = len(offers1)
    offersSize2 = len(offers2)
    numberOfComparisons = offersSize2 if offersSize1 >= offersSize2 else offersSize1
    priceDifferences = []
    for index in range(numberOfComparisons):
        offersPrice1 = offers1[index]["rate"]
        offersPrice2 = offers2[index]["rate"]
        difference = ((offersPrice1 - offersPrice2) / offersPrice1)
        priceDifferences.append(difference)

    return priceDifferences


def printPriceDifference(marketSymbol: Tuple[str, str], tradeOffer: Tuple[dict, dict], operationType: str, difference: float):
    differencePercentage = (1 - difference) * 100
    operationWord = 'Buying from' if operationType == "BUY" else 'Selling on'

    print(f'Difference ratio for {marketSymbol}: ', end="")
    print('{:.4f}'.format(differencePercentage) + '% (' + '{:.4f}'.format(difference * 100) + '%)', sep="")
    print(f"{operationWord} {tradeOffer[0]['title']} instead of {tradeOffer[1]['title']} is", end="")

    if operationType == 'BUY':
        print(f"{'' if difference < 0 else ' not'} worth it as you would {'get additional' if difference < 0 else 'lose'}", end="")
    elif operationType == "SELL":
        print(f"{'' if difference > 0 else ' not'} worth it as you would {'get additional' if difference > 0 else 'lose'}", end="")

    print(f" {'{:.4f}'.format(abs(difference * 100))}%.\n")


def handlePriceDifferences(marketSymbol: Tuple[str, str], tradeOffer: Tuple[dict, dict], operationType: str, offers1: List[dict[str, float]], offers2: List[dict[str, float]]):
    differences = findPriceDifferences(offers1, offers2)
    for dif in differences:
        printPriceDifference(marketSymbol, tradeOffer, operationType, dif)


def printArbitrationDetails(marketSymbol: Tuple[str, str], tradeOffer: Tuple[dict, dict], buyRate: float, sellRate: float, difference: float):
    differenceRatio = 1 - difference
    print(f'The cheapest {marketSymbol[0]} buy rate on {tradeOffer[0]["title"]}: {buyRate}')
    print(f'The most expensive {marketSymbol[0]} sell rate on {tradeOffer[1]["title"]}: {sellRate}')
    print(f'Arbitration ratio for {marketSymbol[0]} -> {marketSymbol[1]}: ' + '{:.4f}'.format(differenceRatio * 100) + '%')
    print(f"The transaction is{'' if difference > 0 else ' not'} worth it as you will have "
          f"{'{:.3f}'.format((1 + difference) * 100)}% of your initial balance.")


def calculateFees(takerApi: dict, transferApi: dict, marketSymbol: Tuple[str, str], volume: float):
    takerFee = takerApi["takerFee"]
    transferFee = transferApi["transferFee"][marketSymbol[0]]
    return volume * takerFee + transferFee


def printAdvArbitrationDetails(marketSymbol: Tuple[str, str], transactionVolume: float, totalFee: float, volumeAfterFees: float, difference: float, differenceRatio: float, profit: float):
    print(f'Transaction volume: {transactionVolume} {marketSymbol[0]}')
    print(f'Total fee: ' + '{:.8f}'.format(totalFee) + f' {marketSymbol[0]}')
    print(f'Transaction volume reduced by fees: ' + '{:.8f}'.format(volumeAfterFees) + f' {marketSymbol[0]}')

    print(f'Arbitration rate: ' + '{:.3f}'.format(differenceRatio) + '% (' + '{:.3f}'.format(difference * 100) + '%)')
    print(f'Profit: ' + '{:.3f}'.format(profit) + f' {marketSymbol[1]}')


def calculateDifference(marketSymbol: Tuple[str, str], apis: Tuple[dict, dict], numberOfOffers: int, refreshDelay: int, operationType: str):
    while True:
        offers1 = getOffers(marketSymbol, numberOfOffers, apis[0])
        offers2 = getOffers(marketSymbol, numberOfOffers, apis[1])
        if offers1 and offers2:
            buyOffers1, sellOffers1 = offers1["asks"], offers1["bids"]
            buyOffers2, sellOffers2 = offers2["asks"], offers2["bids"]

            if operationType == "BUY":
                handlePriceDifferences(marketSymbol, apis, operationType, buyOffers1, buyOffers2)
            elif operationType == "SELL":
                handlePriceDifferences(marketSymbol, apis, operationType, sellOffers1, sellOffers2)
            elif operationType == "ARB" or operationType == "ARB+":
                handlePriceDifferences(marketSymbol, apis, "BUY", buyOffers1, buyOffers2)
                handlePriceDifferences(marketSymbol, apis, "SELL", sellOffers1, sellOffers2)

                cheapestBuy = min(filter(lambda val: val["rate"] is not None, buyOffers1), key=lambda val: val["rate"])
                mostExpensiveSell = max(filter(lambda val: val["rate"] is not None, sellOffers2), key=lambda val: val["rate"])
                difference = (mostExpensiveSell["rate"] - cheapestBuy["rate"]) / cheapestBuy["rate"]
                differenceRatio = (1 - difference) * 100

                if operationType == "ARB":
                    printArbitrationDetails(marketSymbol, apis, cheapestBuy["rate"], mostExpensiveSell["rate"], difference)
                else:
                    transactionVolume = min(cheapestBuy["quantity"], mostExpensiveSell["quantity"])
                    totalFee = calculateFees(apis[0], apis[1], marketSymbol, transactionVolume)
                    volumeAfterFees = transactionVolume - totalFee
                    profitDifference = mostExpensiveSell["rate"] - cheapestBuy["rate"]
                    profit = profitDifference * volumeAfterFees

                    #print(cheapestBuy["rate"] * volumeAfterFees, mostExpensiveSell["rate"] * volumeAfterFees)

                    printAdvArbitrationDetails(marketSymbol, transactionVolume, totalFee, volumeAfterFees, difference, differenceRatio, profit)
        sleep(refreshDelay)


def main():
    baseCurrency = 'USD'
    marketSymbol = ('ETH', baseCurrency)
    tradeOrder = (APIS[0], APIS[1])
    numberOfOffers = 5
    refreshDelay = 20

    operationTypes = ['BUY', 'SELL', 'ARB', 'ARB+']
    operationType = operationTypes[3]
    calculateDifference(marketSymbol, tradeOrder, numberOfOffers, refreshDelay, operationType)


if __name__ == "__main__":
    main()


