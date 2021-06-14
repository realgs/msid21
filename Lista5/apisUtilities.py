import time
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from common import load_data_from_json

NORMALIZED_OPERATIONS = ['bids', 'asks']
WAITING_TIME = 1


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
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
    return set(fstStockPairs).intersection(sndStockPairs)


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


def get_current_foreign_stock_price(stock, baseCurrency, apiInfo):
    try:
        tickerInfo = yf.Ticker(stock).info
        currency = tickerInfo['currency'] if tickerInfo['currency'] else "USD"
        return exchange_base_currency(currency, baseCurrency,
                                      (float(tickerInfo['dayLow']) + float(tickerInfo['dayHigh'])) / 2, apiInfo)
    except Exception:
        raise ValueError(f'Wrong symbol: {stock}')


def get_current_pl_stock_price(stock, baseCurrency, apiInfo):
    stooqUrl = apiInfo["API"]["stooq"]["url_stock"]
    try:
        response = requests.get(f"{stooqUrl}{stock.lower()}").text
        soup = BeautifulSoup(response, 'html.parser')
        price = float(soup.find(id="t1").find('td').find('span').get_text())
        return exchange_base_currency("PLN", baseCurrency, price, apiInfo)

    except Exception:
        raise ValueError(f'Wrong symbol: {stock}')


if __name__ == '__main__':
    data = load_data_from_json("data.json")
    apisInfo = load_data_from_json("apis.json")
    print(exchange_base_currency(data['currencies'][0]["symbol"], data["baseCurrency"],
                                 data['currencies'][0]["quantity"], apisInfo))

    print(get_current_foreign_stock_price(data['foreignStock'][0]["symbol"], data['baseCurrency'], apisInfo))

    print(get_current_pl_stock_price(data["plStock"][0]['symbol'], data['baseCurrency'], apisInfo))


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
    offersToBuyFrom = sourceStock.get_offers()[NORMALIZED_OPERATIONS[1]]
    offersToSellTo = targetStock.get_offers()[NORMALIZED_OPERATIONS[0]]
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

    return {'volume': volume, 'profitability': profitability, 'profit': round(gainedMoney - spentMoney, 5)}


def zad6(fstStock, sndStock, transferFees, currencyPairs):
    resultsFromFstToSnd = []
    resultsFromSndToFst = []
    for currency in currencyPairs:
        crypto = currency[0]
        base_currency = currency[1]
        print(f"Cryptocurrency: {crypto}, base currency: {base_currency}")
        offer1 = fstStock.get_offers()
        offer2 = sndStock.get_offers()
        if offer1 is not None and offer2 is not None:
            if offer1.get(NORMALIZED_OPERATIONS[0], None) and offer1.get(NORMALIZED_OPERATIONS[1], None) \
                    and offer2.get(NORMALIZED_OPERATIONS[0], None) and offer2.get(NORMALIZED_OPERATIONS[1], None):
                print(f'{fstStock.get_name()} - selling offers: {offer1[NORMALIZED_OPERATIONS[1]]}\n'
                      f'{fstStock.get_name()} - buying offers: {offer1[NORMALIZED_OPERATIONS[0]]}')
                print(f'{sndStock.get_name()} - selling offer: {offer2[NORMALIZED_OPERATIONS[1]]}\n'
                      f'{sndStock.get_name()} - buying offers: {offer2[NORMALIZED_OPERATIONS[0]]}')
                resultFrom1To2 = calculate_arbitrage(fstStock, sndStock, crypto, base_currency, transferFees)
                resultsFromFstToSnd.append((crypto, base_currency, resultFrom1To2))
                if resultFrom1To2['profit'] <= 0:
                    print(f"There are no profitable transactions buying in {fstStock.get_name()}"
                          f" and selling in {sndStock.get_name()}")
                else:
                    print(f"Buying from {fstStock.get_name()}:\n "
                          f"Volume: {resultFrom1To2['volume']} {crypto},"
                          f" profit: {resultFrom1To2['profit']} {base_currency},"
                          f" gain: {resultFrom1To2['profitability']}%")
                resultFrom2To1 = calculate_arbitrage(sndStock, fstStock, crypto, base_currency, transferFees)
                resultsFromSndToFst.append((crypto, base_currency, resultFrom2To1))
                if resultFrom2To1['profit'] <= 0:
                    print(f"There are no profitable transactions buying in {sndStock.get_name()}"
                          f" and selling in {fstStock.get_name()}")
                else:
                    print(f"Buying from {sndStock.get_name()}:\n "
                          f"Volume: {resultFrom2To1['volume']} {crypto},"
                          f" profit: {resultFrom2To1['profit']} {base_currency},"
                          f" gain: {resultFrom2To1['profitability']}%")
            else:
                print("Orderbooks do not contain buying and selling prices!")
        else:
            print("Something gone wrong during data acquisition")
        time.sleep(WAITING_TIME)
        print()
    return resultsFromFstToSnd, resultsFromSndToFst
