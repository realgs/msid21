import asyncio
from typing import Tuple, List

import aiohttp
import requests

from constants import APIS, NUMBER_OF_OFFERS


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


async def get(url, client):
    try:
        async with client.get(url=url) as response:
            resp = await response.json()
            return resp
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def getOffersAsync(marketSymbol: Tuple[str, str], numberOfOffers: int, apiObject: dict, client):
    if numberOfOffers <= 0:
        raise Exception("Number of offers should be positive.")

    tradeOffers = await get(apiObject['urlFormatFunction'](apiObject['baseUrl'], marketSymbol, apiObject['orderBookEndpoint']), client)
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


def getOffers(marketSymbol: Tuple[str, str], numberOfOffers: int, apiObject: dict):
    if numberOfOffers <= 0:
        raise Exception("Number of offers should be positive.")

    tradeOffers = fetchData(
        apiObject['urlFormatFunction'](apiObject['baseUrl'], marketSymbol, apiObject['orderBookEndpoint']))
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


def getTransferFees(apiName: str):
    shrinkedBaseUrl = APIS[apiName]["baseUrl"].replace('/markets', '')
    availableCurrencies = fetchData(f"{shrinkedBaseUrl}/{APIS[apiName]['transferFeesEndpoint']}")

    fees = {}
    for curr in availableCurrencies:
        fees[curr["symbol"]] = float(curr["txFee"])

    return fees


def getMarketsNames(apiName: str):
    markets = fetchData(APIS[apiName]["marketsUrl"])
    if markets:
        if isinstance(markets, dict):
            return list(markets[APIS[apiName]["marketsKey"]].keys())
        elif isinstance(markets, list):
            return list(map(lambda market: market[APIS[apiName]["marketsKey"]], markets))
        else:
            raise Exception("Invalid data.")


def findMarketsIntersection(market1: List[str], market2: List[str]):
    return list(set(market1).intersection(set(market2)))


def collectOffers(apiNames: List[str], markets: List[str]):
    offers = {}
    for apiName in apiNames:
        apiOffers = {}
        for market in markets:
            marketSymbol: Tuple[str, str] = tuple(market.split('-')[:2])
            marketOffers = getOffers(marketSymbol, NUMBER_OF_OFFERS, APIS[apiName])
            apiOffers[market] = marketOffers

        offers[apiName] = apiOffers

    return offers


async def collectOffersAsync(apiNames: List[str], markets: List[str]):
    offers = {}
    for apiName in apiNames:
        async with aiohttp.ClientSession() as client:
            apiOffers = {}
            allOffers = await asyncio.gather(*[getOffersAsync(tuple(market.split('-')[:2]), NUMBER_OF_OFFERS, APIS[apiName], client) for market in markets])
            for index, market in enumerate(markets):
                apiOffers[market] = allOffers[index]

        offers[apiName] = apiOffers

    return offers


def calculateFees(takerApi: str, transferApi: str, marketSymbol: Tuple[str, str], volume: float):
    takerFee = APIS[takerApi]["takerFee"]
    transferFee = APIS[transferApi]["transferFee"][marketSymbol[0]]
    return volume * takerFee + transferFee


def findArbitrage(bid: dict, ask: dict, apiNames: Tuple[str, str], marketSymbol: Tuple[str, str]):
    transactionVolume = min(bid["quantity"], ask["quantity"])
    totalFee = calculateFees(apiNames[0], apiNames[1], marketSymbol, transactionVolume)
    volumeAfterFees = transactionVolume - totalFee
    if volumeAfterFees < 0:
        raise ValueError("Not enough volume to perform this action - transaction fees are too high.")

    rateDifference = bid["rate"] - ask["rate"]
    profit = rateDifference * volumeAfterFees
    percentageProfit = profit / (transactionVolume * bid["rate"])

    return volumeAfterFees, totalFee, profit, percentageProfit


def findArbitages(apiNames: Tuple[str, str], exchangeMarkets: dict):
    arbitrageOffers = {}
    for (marketName, offers) in exchangeMarkets[apiNames[0]].items():  # loop through exchange1
        for bid in offers["bids"]:  # loop through given market bids
            for ask in exchangeMarkets[apiNames[1]][marketName]["asks"]:  # loop through exchange2 asks for given market
                # for each bid, loop through all asks and check arbitrage
                try:
                    volumeAfterFees, totalFee, profit, percentageProfit = findArbitrage(bid, ask, apiNames, marketName.split('-'))
                    if profit <= 0:
                        break

                    arbitrageDetails = {
                        'market': marketName,
                        'exchangeMarkets': apiNames,
                        "totalFee": totalFee,
                        'volumeAfterFees': volumeAfterFees,
                        'profit': profit,
                        'percentageProfit': percentageProfit,
                        'bidRate': bid["rate"],
                        'askRate': ask["rate"]
                    }
                    if marketName in arbitrageOffers:
                        arbitrageOffers[marketName].append(arbitrageDetails)
                    else:
                        arbitrageOffers[marketName] = [arbitrageDetails]
                except ValueError:
                    pass

    return arbitrageOffers


def sortArbitrages(*arbitrages: dict):
    listOfArbitrages = []
    for arb in arbitrages:
        listOfArbitrages += sum(arb.values(), [])

    return sorted(listOfArbitrages, key=lambda arbitrage: arbitrage["percentageProfit"], reverse=True)


def printArbitrages(arbitrages1: dict, arbitrages2: dict, limitDisplay: int = None):
    sortedArbitrages = sortArbitrages(arbitrages1, arbitrages2)[:limitDisplay]

    for i, arb in enumerate(sortedArbitrages):
        marketSymbol = arb["market"].split('-')
        transactionVolume = arb["volumeAfterFees"] + arb["totalFee"]
        print(f'{i + 1}. [{arb["exchangeMarkets"][0]} -> {arb["exchangeMarkets"][1]}]', f'[{marketSymbol[0]} -> {marketSymbol[1]}]')
        print(f'Profit ' + '{0:.10f}'.format(arb["profit"]) + f' {marketSymbol[1]} ({"{0:.4f}".format(arb["percentageProfit"] * 100)}% of the initial investment)')
        print(f'Transaction volume: {transactionVolume} {marketSymbol[0]}', f' | Volume after fees: {arb["volumeAfterFees"]} {marketSymbol[0]}')
        print(f'Bid rate: {"{0:.8f}".format(arb["bidRate"])} | Ask rate {"{0:.8f}".format(arb["askRate"])}')
        print(f'Initial investment: {transactionVolume * arb["bidRate"]} {marketSymbol[1]}')
        print()


