from apiConnection import getApiResponse

API_BASE_URL = "https://api.bitbay.net/rest/trading/orderbook-limited/"
STATUS_OK = "Ok"
STATUS_KEY = "status"


def getBestOrders(cryptos):
    apiResult = getApiResponse(f"{API_BASE_URL}/{cryptos[1]}-{cryptos[0]}/10", STATUS_KEY, STATUS_OK)

    if apiResult:
        if apiResult['buy'] and apiResult['sell']:
            buys = apiResult['buy']
            sells = apiResult['sell']
            highestBuy = buys[len(buys)-1]
            lowestSell = sells[0]
            return {"success": True,
                    "buy": {"price": float(highestBuy['ra']), "quantity": float(highestBuy['ca'])},
                    "sell": {"price": float(lowestSell['ra']), "quantity": float(lowestSell['ca'])}}
        else:
            return {"success": False, "cause": "There is not enough data"}
    else:
        return {"success": False, "cause": "Cannot retrieve data"}
