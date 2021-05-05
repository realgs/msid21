from apiConnection import getApiResponse

NAME = "Bittrex"
# https://www.cryptowisser.com/exchange/bittrex/#:~:text=Well%2C%20Bittrex%20is%20one%20of,flat%20trading%20fee%20of%200.20%25.
TAKER_FEE = 0.002
DEFAULT_TRANSFER_FEE = 1
API_BASE_URL = "https://api.bittrex.com/api/v1.1/public/"
SUCCESS_KEY = 'success'
SUCCESS_VALUE = True

__transferFees = {}


def getName():
    return NAME


def getTakerFee():
    return TAKER_FEE


def getTransferFee(currency):
    if currency in __transferFees:
        return __transferFees[currency]
    # https://api.bittrex.com/api/v1.1/public/getcurrencies
    apiResult = getApiResponse(f"{API_BASE_URL}getcurrencies", SUCCESS_KEY, SUCCESS_VALUE)

    if apiResult and apiResult['result']:
        for currencyData in apiResult['result']:
            if currencyData['Currency'] == currency:
                __transferFees[currency] = currencyData['TxFee']
                return currencyData['TxFee']
    return DEFAULT_TRANSFER_FEE


def getBestOrders(cryptos, amount):
    apiResult = getApiResponse(f"{API_BASE_URL}getorderbook?market={cryptos[0]}-{cryptos[1]}&type=both", SUCCESS_KEY, SUCCESS_VALUE)

    if apiResult and apiResult['result']:
        if apiResult['result']['buy'] and apiResult['result']['sell']:
            buys = [{"price": b['Rate'], "quantity": b['Quantity']} for b in apiResult['result']['buy']]
            sells = [{"price": s['Rate'], "quantity": s['Quantity']} for s in apiResult['result']['sell']]
            if len(buys) >= amount and len(sells) >= amount:
                return {"success": True, "buys": buys[:amount], "sells": sells[:amount]}
        else:
            return {"success": False, "cause": "There is not enough data"}
    else:
        return {"success": False, "cause": "Cannot retrieve data"}


def getAvailableMarkets():
    apiResult = getApiResponse(f"{API_BASE_URL}/getmarkets", SUCCESS_KEY, SUCCESS_VALUE)

    if apiResult and apiResult['success'] and apiResult['result']:
        markets = []
        for market in apiResult['result']:
            if not market['IsRestricted']:
                # markets.append({'currency1': market['MarketCurrency'], 'currency2': market['BaseCurrency'], 'minTrade': market['MinTradeSize']})
                markets.append({'currency1': market['MarketCurrency'], 'currency2': market['BaseCurrency']})
        return {"success": True, 'markets': markets}
    else:
        return {"success": False, "cause": "Cannot retrieve data"}
