import time
import yfinance as yf
import requests

import common


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def get_bitrex_fees(apiInfo):
    fees = get_api_response(apiInfo['API']['bitrex']['url_currencies'])
    dictionary = {}
    if fees.get("result", None):
        items = fees['result']
        for entry in items:
            if entry.get('Currency', None) and entry.get('TxFee', None):
                dictionary[entry['Currency']] = entry["TxFee"]

    return dictionary


def get_transfer_fees(apiInfo, pairs):
    fees = {"bitbay": {}, "bitrex": {}}
    bitrexFees = get_bitrex_fees(apiInfo)
    for pair in pairs:
        fees['bitbay'][pair[0]] = apiInfo['FEES']["bitbay_fees"][pair[0]]
        fees['bitrex'][pair[0]] = bitrexFees[pair[0]]
    return fees


def parse_bitbay_currencies(jsonData):
    result = []
    if jsonData.get("items", None):
        items = jsonData['items']
        for entry in items.keys():
            pair = entry.split('-')
            result.append((pair[0], pair[1]))
    return result


def parse_bitrex_currencies(jsonData):
    result = []
    if jsonData.get("result", None):
        for entry in jsonData['result']:
            if entry.get("MarketCurrency", None) and entry.get("BaseCurrency", None):
                result.append((entry['MarketCurrency'], entry['BaseCurrency']))
    return result


def get_currency_pairs(apiInfo, market):
    marketInfo = get_api_response(apiInfo['API'][market]['url_markets'])
    if marketInfo is not None:
        if market == apiInfo['API']['bitbay']['name']:
            return parse_bitbay_currencies(marketInfo)
        elif market == apiInfo['API']['bitrex']['name']:
            return parse_bitrex_currencies(marketInfo)


def find_common_currencies_pairs(apiInfo):
    bitbayPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitbay']['name'])
    bitrexPairs = get_currency_pairs(apiInfo, apiInfo['API']['bitrex']['name'])

    return set(bitrexPairs).intersection(bitbayPairs)


def exchange_base_currency(sourceCurrency, targetCurrency, quantity, apiInfo):
    if sourceCurrency == targetCurrency:
        return quantity
    if sourceCurrency == 'PLN':
        url = f"{apiInfo['API']['nbp']['url_exchange']}{targetCurrency}/{apiInfo['API']['nbp']['json_format']}"
        response = get_api_response(url)
        return quantity / float(response['rates'][0]['ask'])
    elif targetCurrency == 'PLN':
        url = f"{apiInfo['API']['nbp']['url_exchange']}{sourceCurrency}/{apiInfo['API']['nbp']['json_format']}"
        response = get_api_response(url)
        return quantity * float(response['rates'][0]['bid'])

    plnValue = exchange_base_currency(sourceCurrency, 'PLN', quantity, apiInfo)
    return exchange_base_currency('PLN', targetCurrency, plnValue, apiInfo)


if __name__ == '__main__':
    data = common.load_data_from_json("data.json")
    apisInfo = common.load_data_from_json("apis.json")
    print(round(exchange_base_currency(data['currencies'][0]["symbol"], data["baseCurrency"], data['currencies'][0]["quantity"], apisInfo), 2))
    print(yf.Ticker("AAPL").info)


NORMALIZED_OPERATIONS = ['bids', 'asks']
WAITING_TIME = 3


def parse_bitrex_orderbook(jsonData):
    resultDictionary = {}
    if jsonData.get("result", None):
        table = []
        if jsonData["result"].get("buy", None):
            pair = []
            for dictionary in jsonData["result"]["buy"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[0]] = table.copy()
            table.clear()
        if jsonData["result"].get("sell", None):
            pair = []
            for dictionary in jsonData["result"]["sell"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[1]] = table.copy()
            table.clear()
    return resultDictionary


def get_offers(currency, market, baseCurrency, apiInfo):
    if market == apiInfo["API"]["bitbay"]["name"]:
        offers = get_api_response(f'{apiInfo["API"]["bitbay"]["url_orderbook"]}{currency}'
                                  f'{baseCurrency}{apiInfo["API"]["bitbay"]["orderbook_ending"]}')
        if offers is not None:
            return offers

    elif market == apiInfo["API"]["bitrex"]["name"]:
        offers = get_api_response(f'{apiInfo["API"]["bitrex"]["url_orderbook"]}{baseCurrency}'
                                  f'{apiInfo["API"]["bitrex"]["orderbook_separator"]}'
                                  f'{currency}{apiInfo["API"]["bitrex"]["orderbook_ending"]}')
        if offers is not None:
            return parse_bitrex_orderbook(offers)

    else:
        return None


def calculate_percentage_difference(order1, order2):
    return round(((order1 - order2) / order1) * 100, 2)


def include_taker_fee(cost, market, operation):
    if operation == NORMALIZED_OPERATIONS[1]:
        return cost * (1 + market["taker_fee"])
    elif operation == NORMALIZED_OPERATIONS[0]:
        return cost * (1 - market["taker_fee"])


def calculate_order_value(price, amount):
    return price * amount


def calculate_arbitrage(offersToBuyFrom, offersToSellTo, buyingMarket, sellingMarket, currency, baseCurrency, fees):
    volume = 0.0
    spentMoney = 0.0
    gainedMoney = 0.0
    transferFee = fees[buyingMarket['name']][currency]
    transferFeePaidNumber = 0
    operationNumber = 0

    while offersToBuyFrom and offersToSellTo and offersToBuyFrom[0][0] < offersToSellTo[0][0]:
        operationNumber += 1
        buyVolume = min(offersToBuyFrom[0][1], offersToSellTo[0][1])
        sellVolume = buyVolume
        if transferFee > 0:
            if sellVolume > transferFee:
                sellVolume -= transferFee
                transferFee = 0
                transferFeePaidNumber = operationNumber
            else:
                transferFee -= buyVolume
                sellVolume = 0
        buyValue = calculate_order_value(offersToBuyFrom[0][0], buyVolume)
        buyCost = include_taker_fee(buyValue, buyingMarket, NORMALIZED_OPERATIONS[1])
        sellValue = calculate_order_value(offersToSellTo[0][0], sellVolume)
        sellGain = include_taker_fee(sellValue, sellingMarket, NORMALIZED_OPERATIONS[0])

        if buyCost < sellGain or transferFee > 0 or (transferFee == 0.0 and operationNumber == transferFeePaidNumber):
            volume += buyVolume
            spentMoney += buyCost
            gainedMoney += sellGain

            if transferFee > 0 or (transferFee == 0.0 and operationNumber == transferFeePaidNumber):
                print(f" Checking for negative profit until transfer fee is covered:"
                      f" {round(gainedMoney - spentMoney, 5)} {baseCurrency}")

            offersToSellTo[0][1] -= sellVolume
            if offersToSellTo[0][1] == 0:
                del offersToSellTo[0]
            offersToBuyFrom[0][1] -= buyVolume
            if offersToBuyFrom[0][1] == 0:
                del offersToBuyFrom[0]

        else:
            break

    if gainedMoney < spentMoney:
        gainedMoney = spentMoney = 0
    if spentMoney == 0 and gainedMoney == 0:
        profitability = 0
    else:
        profitability = round(((gainedMoney - spentMoney) / spentMoney) * 100, 2)

    return {'volume': volume, 'profitability': profitability, 'profit': round(gainedMoney - spentMoney, 2)}


def zad3(apiInfo, transferfees, currencypairs):
    resultsFromBitbayToBitrex = []
    resultsFromBitrexToBitbay = []
    for currency in currencypairs:
        crypto = currency[0]
        base_currency = currency[1]
        print(f"Cryptocurrency: {crypto}, base currency: {base_currency}")
        i = 0
        offer1 = get_offers(crypto, apiInfo["API"]["bitbay"]["name"], base_currency, apiInfo)
        offer2 = get_offers(crypto, apiInfo["API"]["bitrex"]["name"], base_currency, apiInfo)
        if offer1 is not None and offer2 is not None:
            if offer1.get(NORMALIZED_OPERATIONS[0], None) and offer1.get(NORMALIZED_OPERATIONS[1], None) \
                    and offer2.get(NORMALIZED_OPERATIONS[0], None) and offer2.get(NORMALIZED_OPERATIONS[1], None):
                print(f'{apiInfo["API"]["bitbay"]["name"]} - selling offers: {offer1[NORMALIZED_OPERATIONS[1]]}\n'
                      f'{apiInfo["API"]["bitbay"]["name"]} - buying offers: {offer1[NORMALIZED_OPERATIONS[0]]}')
                print(f'{apiInfo["API"]["bitrex"]["name"]} - selling offer: {offer2[NORMALIZED_OPERATIONS[1]]}\n'
                      f'{apiInfo["API"]["bitrex"]["name"]} - buying offers: {offer2[NORMALIZED_OPERATIONS[0]]}')
                resultFrom1To2 = calculate_arbitrage(offer1[NORMALIZED_OPERATIONS[1]],
                                                     offer2[NORMALIZED_OPERATIONS[0]],
                                                     apiInfo["API"]["bitbay"], apiInfo["API"]["bitrex"], crypto,
                                                     base_currency, transferfees)
                resultsFromBitbayToBitrex.append((crypto, base_currency, resultFrom1To2))
                if resultFrom1To2['profit'] <= 0:
                    print(f"There are no profitable transactions buying in {apiInfo['API']['bitbay']['name']}"
                          f" and selling in {apiInfo['API']['bitrex']['name']}")
                else:
                    print(f"Buying from {apiInfo['API']['bitbay']['name']}:\n "
                          f"Volume: {resultFrom1To2['volume']} {crypto},"
                          f" profit: {resultFrom1To2['profit']} {base_currency},"
                          f" gain: {resultFrom1To2['profitability']}%")
                resultFrom2To1 = calculate_arbitrage(offer2[NORMALIZED_OPERATIONS[1]],
                                                     offer1[NORMALIZED_OPERATIONS[0]],
                                                     apiInfo["API"]["bitrex"], apiInfo["API"]["bitbay"], crypto,
                                                     base_currency, transferfees)
                resultsFromBitrexToBitbay.append((crypto, base_currency, resultFrom2To1))
                if resultFrom2To1['profit'] <= 0:
                    print(f"There are no profitable transactions buying in {apiInfo['API']['bitrex']['name']}"
                          f" and selling in {apiInfo['API']['bitbay']['name']}")
                else:
                    print(f"Buying from {apiInfo['API']['bitrex']['name']}:\n "
                          f"Volume: {resultFrom2To1['volume']} {crypto},"
                          f" profit: {resultFrom2To1['profit']} {base_currency},"
                          f" gain: {resultFrom2To1['profitability']}%")
            else:
                print("Orderbooks do not contain buying and selling prices!")
        else:
            print("Something gone wrong during data acquisition")
        time.sleep(WAITING_TIME)
        i += 1
        print()
    return resultsFromBitbayToBitrex, resultsFromBitrexToBitbay
