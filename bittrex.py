from apiConnection import getApiResponse

API_BASE_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook"
SUCCESS_KEY = 'success'
SUCCESS_VALUE = True


def getBestOrders(cryptos):
    apiResult = getApiResponse(f"{API_BASE_URL}?market={cryptos[0]}-{cryptos[1]}&type=both", SUCCESS_KEY, SUCCESS_VALUE)

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
