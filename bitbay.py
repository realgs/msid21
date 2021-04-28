from apiConnection import getApiResponse

NAME = "Bitbay"
TAKER_FEE = 0.001
DEFAULT_TRANSFER_FEE = 1
# https://bitbay.net/en/fees#withdrawal-fee
WITHDRAWAL_FEES = {"AAVE": 0.1, "ALG": 157.0, "AMLT": 1176.0, "BAT": 61.0, "BCC": 0.001, "BCP": 732.0, "BOB": 3344.0,
                   "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.0001, "DAI": 0.1, "DASH": 0.001, "DOT": 0.1,
                   "EOS": 0, "ETH": 0.01, "EUR": 2.0, "EXY": 520.0, "GAME": 114, "GBP": 2.0, "GGC": 32.0, "GNT": 150.0,
                   "GRT": 0.1, "LINK": 1.45, "LML": 1.45, "LSK": 0.3, "LTC": 0.001, "LUNA": 0.1, "MANA": 0.1,
                   "MKR": 0.022, "NEU": 360.0, "NPXS": 5082.0, "OMG": 13.0, "PAY": 460.0, "PLN": 10.0, "QARK": 742.0,
                   "REP": 2.1, "SRN": 606.0, "SUSHI": 0.1, "TRX": 1.0, "UNI": 0.0000001, "USDC": 42.0, "USDT": 78.0,
                   "XBX": 1243.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 63.0}

API_BASE_URL = "https://api.bitbay.net/rest/trading/"
STATUS_OK = "Ok"
STATUS_KEY = "status"


def getName():
    return NAME


def getTakerFee():
    return TAKER_FEE


def getTransferFee(currency):
    if currency in WITHDRAWAL_FEES:
        return WITHDRAWAL_FEES[currency]
    return DEFAULT_TRANSFER_FEE


def getBestOrders(cryptos):
    apiResult = getApiResponse(f"{API_BASE_URL}orderbook-limited/{cryptos[1]}-{cryptos[0]}/10", STATUS_KEY, STATUS_OK)

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


def getAvailableMarkets():
    apiResult = getApiResponse(f"{API_BASE_URL}stats", STATUS_KEY, STATUS_OK)

    if apiResult and apiResult['status'] == 'Ok' and apiResult['items']:
        markets = []
        for marketKeys in apiResult['items']:
            split = marketKeys.split('-')
            if split and len(split) == 2:
                markets.append({'currency1': split[0], 'currency2': split[1]})
            else:
                print("Error, incorrect numer of lines")
        return {"success": True, 'markets': markets}
    else:
        return {"success": False, "cause": "Cannot retrieve data"}
