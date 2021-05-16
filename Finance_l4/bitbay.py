import json

import requests


NAME = "BitBay"
BITBAY_URL = "https://api.bitbay.net/rest/trading/"
#BITBAY_URL = 'https://api.bitbay.net/rest/trading/orderbook-limited/'
HEADERS = {'content-type': 'application/json'}
LIMIT = 50
BITBAY_FEES = {
    "taker_fee": 0.0043,
    "transfer_fee_btc": 0.0005
}

def createMarketsList():
    markets_data = getMarketsData()
    markets = []
    markets_data_keys = markets_data['items'].keys()
    for key in markets_data_keys:
        markets.append(key)
    return markets


def getMarketsData():
    #markets_list = []
    url = f'{BITBAY_URL}ticker'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def printJSON(obj):
    msg = json.dumps(obj, indent=4)
    print(msg)


def getOrderbookData(currency_1, currency_2):
    url = f'{BITBAY_URL}orderbook-limited/{currency_1}-{currency_2}/{LIMIT}'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getBestSellBuy(currency_1, currency_2):
    best_sell_buy_list = []
    orders = getOrderbookData(currency_1, currency_2)
    if orders:
        for i in range(0, LIMIT):
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


if __name__ == "__main__":
    #printBestSellBuy(getBestSellBuy("BTC", "USD"), "BTC", "USD")
    markets_list = createMarketsList()
    print(markets_list)