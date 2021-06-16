import time
import requests
import yfinance as yf
from bs4 import BeautifulSoup


NORMALIZED_OPERATIONS = ['bids', 'asks']
WAITING_TIME = 2


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        # print("Request not successful: " + response.reason)
        return None


def get_transfer_fees(stockFst, stockSnd, pairs):
    fees = {stockFst.get_name(): {}, stockSnd.get_name(): {}}
    fstStockFees = stockFst.get_withdrawal_fees()
    sndStockFees = stockSnd.get_withdrawal_fees()
    for pair in pairs:
        fees[stockFst.get_name()][pair[0]] = fstStockFees[pair[0]]
        fees[stockSnd.get_name()][pair[0]] = sndStockFees[pair[0]]
    return fees


def find_common_currencies_pairs(fstStockPairs, sndStockPairs):
    common = []
    for pair in fstStockPairs:
        if pair in sndStockPairs:
            common.append(pair)
    return common


def exchange_base_currency(sourceCurrency, targetCurrency, quantity, apiInfo):
    exchangeRate = get_currency_exchange_rate(sourceCurrency, targetCurrency, apiInfo)
    return exchangeRate * quantity


def get_currency_exchange_rate(sourceCurrency, targetCurrency, apiInfo):
    if sourceCurrency == targetCurrency:
        return 1
    if sourceCurrency == 'PLN':
        url = f"{apiInfo['API']['nbp']['url_exchange']}{targetCurrency}/{apiInfo['API']['nbp']['json_format']}"
        response = get_api_response(url)
        if response is not None:
            return 1 / float(response['rates'][0]['mid'])
        else:
            return None
    elif targetCurrency == 'PLN':
        url = f"{apiInfo['API']['nbp']['url_exchange']}{sourceCurrency}/{apiInfo['API']['nbp']['json_format']}"
        response = get_api_response(url)
        if response is not None:
            return float(response['rates'][0]['mid'])
        else:
            return None

    plnValue = get_currency_exchange_rate(sourceCurrency, 'PLN', apiInfo)
    targetValue = get_currency_exchange_rate('PLN', targetCurrency, apiInfo)
    if plnValue and targetValue:
        return plnValue * targetValue
    else:
        return None


def get_current_foreign_stock_price(stock, baseCurrency, apiInfo):
    # foreign stock prices are checked using yahoo finance API replacement
    try:
        tickerInfo = yf.Ticker(stock).info
        currency = tickerInfo['currency'] if tickerInfo['currency'] else "USD"
        return exchange_base_currency(currency, baseCurrency,
                                      (float(tickerInfo['dayLow']) + float(tickerInfo['dayHigh'])) / 2, apiInfo)
    except Exception:
        raise ValueError(f'Wrong symbol: {stock}')


def get_foreign_exchange(stock):
    # foreign market name is checked using yahoo finance API replacement
    try:
        tickerInfo = yf.Ticker(stock).info
        return tickerInfo['exchange']

    except Exception:
        raise ValueError(f'Wrong symbol: {stock}')


def get_current_pl_stock_price(stock, baseCurrency, apiInfo):
    # due to lack of free API for checking pl stock prices is resolved using HTML scrapping
    stooqUrl = apiInfo["API"]["stooq"]["url_stock"]
    try:
        response = requests.get(f"{stooqUrl}{stock.lower()}").text
        soup = BeautifulSoup(response, 'html.parser')
        price = float(soup.find(id="t1").find(id='f13').find('span').get_text())
        return exchange_base_currency("PLN", baseCurrency, price, apiInfo)

    except Exception:
        raise ValueError(f'Wrong symbol: {stock}')


def calculate_percentage_difference(order1, order2):
    return round(((order1 - order2) / order1) * 100, 2)


def include_taker_fee(cost, stock, operation):
    if operation == NORMALIZED_OPERATIONS[1]:
        return cost * (1 + stock.get_taker_fee())
    elif operation == NORMALIZED_OPERATIONS[0]:
        return cost * (1 - stock.get_taker_fee())


def calculate_order_value(price, amount):
    return price * amount


def calculate_arbitrage(sourceStock, targetStock, currency, baseCurrency, fees):
    offersToBuyFrom = sourceStock.get_offers(currency, baseCurrency)[NORMALIZED_OPERATIONS[1]]
    offersToSellTo = targetStock.get_offers(currency, baseCurrency)[NORMALIZED_OPERATIONS[0]]
    volume = 0.0
    spentMoney = 0.0
    gainedMoney = 0.0
    transferFee = fees[sourceStock.get_name()][currency]
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
        buyCost = include_taker_fee(buyValue, sourceStock, NORMALIZED_OPERATIONS[1])
        sellValue = calculate_order_value(offersToSellTo[0][0], sellVolume)
        sellGain = include_taker_fee(sellValue, targetStock, NORMALIZED_OPERATIONS[0])

        if buyCost < sellGain or transferFee > 0 or (transferFee == 0.0 and operationNumber == transferFeePaidNumber):
            volume += buyVolume
            spentMoney += buyCost
            gainedMoney += sellGain

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

    return {'volume': volume, 'profitability': profitability, 'profit': round(gainedMoney - spentMoney, 5)}


def zad6(fstStock, sndStock, transferFees, currencyPairs):
    resultsFromFstToSnd = []
    resultsFromSndToFst = []
    for currency in currencyPairs:
        crypto = currency[0]
        baseCurrency = currency[1]
        print(f"Checking arbitrage for Cryptocurrency: {crypto}, base currency: {baseCurrency}")
        offer1 = fstStock.get_offers(crypto, baseCurrency)
        offer2 = sndStock.get_offers(crypto, baseCurrency)
        if offer1 is not None and offer2 is not None:
            if offer1.get(NORMALIZED_OPERATIONS[0], None) and offer1.get(NORMALIZED_OPERATIONS[1], None) \
                    and offer2.get(NORMALIZED_OPERATIONS[0], None) and offer2.get(NORMALIZED_OPERATIONS[1], None):
                resultFrom1To2 = calculate_arbitrage(fstStock, sndStock, crypto, baseCurrency, transferFees)
                resultsFromFstToSnd.append((fstStock.get_name(),
                                            sndStock.get_name(), crypto, baseCurrency, resultFrom1To2))
                resultFrom2To1 = calculate_arbitrage(sndStock, fstStock, crypto, baseCurrency, transferFees)
                resultsFromSndToFst.append((sndStock.get_name(),
                                            fstStock.get_name(), crypto, baseCurrency, resultFrom2To1))
            else:
                print("Orderbooks do not contain buying and selling prices!")
        else:
            print("Something gone wrong during data acquisition")
        time.sleep(WAITING_TIME)
    print()
    return resultsFromFstToSnd + resultsFromSndToFst
