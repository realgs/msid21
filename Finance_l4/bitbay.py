import json

import requests


NAME = "BitBay"
BITBAY_URL = "https://api.bitbay.net/rest/trading/"
HEADERS = {'content-type': 'application/json'}
LIMIT = 50
BITBAY_FEES = {
    "taker_fee": 0.0043,
    "transfer_fee": {
        "AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0,
        "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1,
        "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0,
        "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0,
        "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0,
        "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0
    }
}


def createMarketsList():
    markets_data = getMarketsData()
    markets = []
    markets_data_keys = markets_data['items'].keys()
    for key in markets_data_keys:
        markets.append(key)
    return markets


def getMarketsData():
    url = f'{BITBAY_URL}ticker'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getOrderbookData(currency_1, currency_2):
    url = f'{BITBAY_URL}orderbook-limited/{currency_1}-{currency_2}/{LIMIT}'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getBestSellBuy(currency_1, currency_2):
    limit = 50
    best_sell_buy_list = []
    orders = getOrderbookData(currency_1, currency_2)
    if orders:
        if len(orders['sell']) < limit or len(orders['buy']) < limit:
            limit = min(len(orders['sell']), len(orders['buy']))
        for i in range(0, limit):
            sell = orders['sell'][i]
            buy = orders['buy'][len(orders['buy']) - 1 - i]
            sell_buy = sell, buy
            best_sell_buy_list.append(sell_buy)
        return best_sell_buy_list
    else:
        print("There was no data!")
        return None


def printBestSellBuy(best_sell_buy_list, currency_1, currency_2):
    if best_sell_buy_list:
        print('\nOrders from BitBay:')
        number = 1
        for element in best_sell_buy_list:
            sell_rate = element[0]['ra']
            sell_quantity = element[0]['ca']
            buy_rate = element[1]['ra']
            buy_quantity = element[1]['ca']
            print(f'Sell order no.{number} for {currency_1}-{currency_2}: rate: {sell_rate}, amount: {sell_quantity}')
            print(f'Buy order no.{number} for {currency_1}-{currency_2}: rate: {buy_rate}, amount: {buy_quantity}\n')
            number += 1
        else:
            print("There was no data to print")
