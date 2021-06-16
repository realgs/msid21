import requests
import constants_alphavantage
import constants


def get_stock_price(symbol):
    url = constants_alphavantage.URL + constants_alphavantage.INTRADAY + symbol + constants_alphavantage.INTERVAL + constants_alphavantage.KEY
    response = requests.get(url)
    result = {}
    if response.status_code == constants.OK_RESPONSE:
        response = response.json()
        try:
            result[constants.STATUS] = constants_alphavantage.OK
            all_periods = list(response[constants_alphavantage.TIME_SERIES].items())
            last = all_periods[0]
            price = last[1][constants_alphavantage.HIGH]
            result[constants_alphavantage.PRICE] = float(price)
        except:
            result[constants.STATUS] = constants_alphavantage.NO_STOCK
    else:
        result[constants.STATUS] = response.status_code
    return result


def get_offer(base_currency, quote_currency):
    url = constants_alphavantage.URL + constants_alphavantage.CURRENCY_EXCHANGE + constants_alphavantage.BASE_CURRENCY + base_currency + constants_alphavantage.QUOTE_CURRENCY + quote_currency + constants_alphavantage.KEY
    response = requests.get(url)
    result = {}
    if response.status_code == constants.OK_RESPONSE:
        response = response.json()
        try:
            result[constants.STATUS] = constants_alphavantage.OK
            bid = response['Realtime Currency Exchange Rate']['8. Bid Price']
            ask = response['Realtime Currency Exchange Rate']['9. Ask Price']
            result[constants.ASK] = float(ask)
            result[constants.BID] = float(bid)
        except:
            result[constants.STATUS] = constants_alphavantage.NO_CURRENCY_PAIR
    else:
        result[constants.STATUS] = response.status_code
    return result
