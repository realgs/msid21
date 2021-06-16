import requests

API = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&apikey=CDQPLS6W3KKJ09YP"
NBP = "http://api.nbp.pl/api/exchangerates/rates/c/{}"

def getExchangeBid():
    try:
        req = requests.get(NBP.format("USD"))
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
        rates = requests.get(NBP.format(curr))
        if 199 < rates.status_code < 300:
            exchange_rate = rates.json()
            return exchange_rate['rates'][0]['ask']
        else:
            print("Error")
            return None
    except Exception:
        return None

def change(amount, baseCurr):
    valPLN = getExchangeBid() * amount
    if baseCurr != "PLN":
        value = valPLN / getExchangeAsk(baseCurr)
        return value
    else:
        return valPLN

def getBid(stock_name):
    try:
        req = requests.get(API.format(stock_name))
        if 199 < req.status_code < 300:
            temp = list(req.json().items())
            bid = list((temp[1][1]).items())[1][1]
            return float(bid['2. high'])
        else:
            print("Response error")
            return None
    except requests.exceptions.ConnectionError:
        print("Connection error")
        return None

def calculateValue(stock, baseCurr, quantity, percent=100):
    part = None
    bid = getBid(stock)
    amount = quantity * bid
    value = change(amount, baseCurr)
    if percent != 100:
        part = (quantity * percent/100) * bid
    bestPlace = "alphavantage"
    return round(value, 3), bid, part, bestPlace
