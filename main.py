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


def findPriceDifference(offers1: List[dict[str, float]], offers2: List[dict[str, float]]):
    offersSize1 = len(offers1)
    offersSize2 = len(offers2)
    numberOfComparisons = offersSize2 if offersSize1 >= offersSize2 else offersSize1

    for index in range(numberOfComparisons):
        offersPrice1 = offers1[index]["rate"]
        offersPrice2 = offers2[index]["rate"]

        difference = ((offersPrice1 - offersPrice2) / offersPrice1)
        return difference


def printPriceDifference(marketSymbol: Tuple[str, str], tradeOffer: Tuple[dict, dict], operationType: str, difference: float):
    differencePercentage = (1 - difference) * 100
    print(f'Difference for {marketSymbol}: ', end="")
    print('{:.4f}'.format(differencePercentage) + '% (' + '{:.4f}'.format(difference * 100) + '%)', sep="")

    if operationType == 'BUY':
        print(
            f"Buying from {tradeOffer[0]['title']} instead of {tradeOffer[1]['title']} is{'' if difference < 0 else ' not'} worth it as you would {'get additional' if difference < 0 else 'lose'} {'{:.4f}'.format(abs(difference * 100))}%.\n")
    elif operationType == "SELL":
        print(
            f"Selling on {tradeOffer[0]['title']} instead of {tradeOffer[1]['title']} is{'' if difference > 0 else ' not'} worth it as you would {'get additional' if difference > 0 else 'lose'} {'{:.4f}'.format(abs(difference * 100))}%.\n")


def calculateFees(takerApi: dict, transferApi: dict, marketSymbol: Tuple[str, str], volume: float):
    takerFee = takerApi["takerFee"]
    transferFee = transferApi["transferFee"][marketSymbol[0]]
    return volume * takerFee + transferFee


def calculateDifference(marketSymbol: Tuple[str, str], apis: Tuple[dict, dict], numberOfOffers: int, refreshDelay: int,
                        operationType: str):
    while True:
        offers1 = getOffers(marketSymbol, numberOfOffers, apis[0])
        offers2 = getOffers(marketSymbol, numberOfOffers, apis[1])
        if offers1 and offers2:
            buyOffers1 = offers1["asks"]
            sellOffers1 = offers1["bids"]
            buyOffers2 = offers2["asks"]
            sellOffers2 = offers2["bids"]

            if operationType == "BUY":
                difference = findPriceDifference(buyOffers1, buyOffers2)
                print(difference)
                printPriceDifference(marketSymbol, apis, operationType, difference)
            elif operationType == "SELL":
                difference = findPriceDifference(sellOffers1, sellOffers1)
                printPriceDifference(marketSymbol, apis, operationType, difference)
            elif operationType == "ARB":
                # findPriceDifference(marketSymbol, apis, buyOffers1, buyOffers2, "BUY")
                # findPriceDifference(marketSymbol, apis, sellOffers1, sellOffers2, "SELL")

                cheapestBuy = min(filter(lambda val: val["rate"] is not None, buyOffers1), key=lambda val: val["rate"])
                mostExpensiveSell = max(filter(lambda val: val["rate"] is not None, sellOffers2),
                                        key=lambda val: val["rate"])
                difference = (mostExpensiveSell["rate"] - cheapestBuy["rate"]) / cheapestBuy["rate"]
                differenceRatio = (1 - difference)

                print(f'The cheapest {marketSymbol[0]} buy rate on {apis[0]["title"]}: {cheapestBuy["rate"]}')
                print(
                    f'The most expensive {marketSymbol[0]} sell rate on {apis[1]["title"]}: {mostExpensiveSell["rate"]}')
                print(f'Arbitration ratio for {marketSymbol[0]} -> {marketSymbol[1]}: '
                      + '{:.3f}'.format(differenceRatio * 100) + '%')

                print(f"The transaction is{'' if difference > 0 else ' not'} worth it as you will have "
                      f"{'{:.3f}'.format((1 + difference) * 100)}% of your initial balance.")

            else:
                cheapestBuy = min(filter(lambda val: val["rate"] is not None, buyOffers1), key=lambda val: val["rate"])
                mostExpensiveSell = max(filter(lambda val: val["rate"] is not None, sellOffers2),
                                        key=lambda val: val["rate"])

                transactionVolume = min(cheapestBuy["quantity"], mostExpensiveSell["quantity"])
                totalFee = calculateFees(apis[0], apis[1], marketSymbol, transactionVolume)
                print(f'Transaction volume: {transactionVolume} {marketSymbol[0]}')
                print(f'Total fee: ' + '{:.8f}'.format(totalFee) + f' {marketSymbol[0]}')
                transactionVolume -= totalFee
                print(f'Transaction volume reduced by fees: {transactionVolume} {marketSymbol[0]}')

                # percentage difference
                difference = (mostExpensiveSell["rate"] - cheapestBuy["rate"]) / cheapestBuy["rate"]
                differenceRatio = (1 - difference) * 100
                print(f'Arbitration rate: {differenceRatio}%')
                # profit difference
                profitDifference = cheapestBuy["rate"] - mostExpensiveSell["rate"]
                profit = profitDifference * transactionVolume
                print(f'Profit: {profit} {marketSymbol[1]}')

        sleep(refreshDelay)


def main():
    baseCurrency = 'ETH'
    marketSymbol = ('XLM', baseCurrency)

    tradeOrder = (APIS[0], APIS[1])
    numberOfOffers = 5
    refreshDelay = 20
    calculateDifference(marketSymbol, tradeOrder, numberOfOffers, refreshDelay, "BUY")
    # calculateDifference(marketSymbol, tradeOrder, numberOfOffers, refreshDelay, "ARB+")


if __name__ == "__main__":
    main()
