import requests
import json
import constants

def pairBB(pair) :
    separated = pair.split()
    return(separated[0]+separated[1])

def pairBT(pair) :
    separated = pair.split()
    return(separated[0]+'-'+separated[1])

def takeBestBB(pair) :
    result = [] #[[bid, amount], [ask, amount]]
    response = requests.get(constants.BITBAY_PUBLIC+pair+constants.BITBAY_ORDERBOOK)
    if response.status_code == constants.CORRECT_RESPONSE :
        j_response = response.json()
        if constants.BITBAY_BIDS in j_response and constants.BITBAY_ASKS in j_response :
            result = [j_response[constants.BITBAY_BIDS][0], j_response[constants.BITBAY_ASKS][0]]
        else :
            result = [constants.ERROR_STATUS, constants.ERROR_NO_ORDERBOOK]
    else :
        result = [constants.ERROR_STATUS, response.status_code]
    return result

def takeBestBT(pair) :
    result = [] #[[bid, amount], [ask, amount]]
    response = requests.get(constants.BITTREX_PUBLIC+pair+constants.BITTREX_ORDERBOOK)
    if response.status_code == constants.CORRECT_RESPONSE :
        j_response = response.json()
        if constants.BITTREX_BID in j_response and constants.BITTREX_ASK in j_response :
            result = [[float(j_response[constants.BITTREX_BID][0][constants.BITTREX_RATE]), float(j_response[constants.BITTREX_BID][0][constants.BITTREX_QUANTITY])], [float(j_response[constants.BITTREX_ASK][0][constants.BITTREX_RATE]), float(j_response[constants.BITTREX_ASK][0][constants.BITTREX_QUANTITY])]]
        else :
            result = [constants.ERROR_STATUS, constants.ERROR_NO_ORDERBOOK]
    else :
        result = [constants.ERROR_STATUS, response.status_code]
    return result
