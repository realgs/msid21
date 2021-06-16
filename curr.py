import requests
API = "http://api.nbp.pl/api/exchangerates/rates/c/{}"


def getExchangeBid(curr):
    try:
        req = requests.get(API.format(curr))
        if 199 < req.status_code < 300:
            exchange_rate = req.json()
            return exchange_rate['rates'][0]['bid']
        else:
            print("Response error")
            return None
    except requests.exceptions.ConnectionError:
        print("Connection error")
        return None

def getExchangeAsk(curr):
    try:
        rates = requests.get(API.format(curr))
        if 199 < rates.status_code < 300:
            exchange_rate = rates.json()
            return exchange_rate['rates'][0]['ask']
        else:
            print("Error")
            return None
    except Exception:
        return None

def change(curr, baseCurr, amount):
    valPLN = getExchangeBid(curr) * amount
    if baseCurr != "PLN":
        value = valPLN / getExchangeAsk(baseCurr)
        return value
    else:
        return valPLN

def calculateValue(currency, baseCurr, quantity, percent=100):
    part = None
    value = change(currency, baseCurr, quantity)
    if baseCurr != "PLN":
        rate = getExchangeBid(currency) / getExchangeAsk(baseCurr)
    else:
        rate = getExchangeBid(currency)
    if percent != 100:
        part = change(currency, baseCurr, quantity * percent/100)
    bestPlace = "NBP"
    return round(value,3), round(rate, 3), part, bestPlace
