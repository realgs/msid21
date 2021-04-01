from apiConnection import getApiResponse

NAME = "Bittrex"
# https://www.cryptowisser.com/exchange/bittrex/#:~:text=Well%2C%20Bittrex%20is%20one%20of,flat%20trading%20fee%20of%200.20%25.
TAKER_FEE = 0.002
DEFAULT_TRANSFER_FEE = 1
API_BASE_URL = "https://api.bittrex.com/api/v1.1/public/"
SUCCESS_KEY = 'success'
SUCCESS_VALUE = True


def getName():
    return NAME


def getTakerFee():
    return TAKER_FEE


def getTransferFee(currency):
    # https://api.bittrex.com/api/v1.1/public/getcurrencies
    apiResult = getApiResponse(f"{API_BASE_URL}getcurrencies", SUCCESS_KEY, SUCCESS_VALUE)

    if apiResult and apiResult['result']:
        for currencyData in apiResult['result']:
            if currencyData['Currency'] == currency:
                return currencyData['TxFee']
    return DEFAULT_TRANSFER_FEE


def getBestOrders(cryptos):
    apiResult = getApiResponse(f"{API_BASE_URL}getorderbook?market={cryptos[0]}-{cryptos[1]}&type=both", SUCCESS_KEY, SUCCESS_VALUE)

    if apiResult and apiResult['result']:
        if apiResult['result']['buy'] and apiResult['result']['sell']:
            buys = apiResult['result']['buy']
            sells = apiResult['result']['sell']
            highestBuy = buys[0]
            lowestSell = sells[0]

            return {"success": True,
                    "buy": {"price": highestBuy['Rate'], "quantity": highestBuy['Quantity']},
                    "sell": {"price": lowestSell['Rate'], "quantity": lowestSell['Quantity']}}
        else:
            return {"success": False, "cause": "There is not enough data"}
    else:
        return {"success": False, "cause": "Cannot retrieve data"}
