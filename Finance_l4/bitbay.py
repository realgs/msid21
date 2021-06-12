import requests


NAME = "BitBay"
BITBAY_URL = "https://api.bitbay.net/rest/trading/"
HEADERS = {'content-type': 'application/json'}
LIMIT = 50
BITBAY_FEES = {
    "taker_fee": 0.0043,
    "transfer_fee": {
        'AAVE': 0.27, 'ALG': 140.0, 'AMLT': 700.0,
        'BAT': 25.0, 'BCC': 0.001, 'BCP': 300.0, 'BOB': 3500.0, 'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001,
        'CHZ': 76.0, 'COMP': 0.5,
        'DAI': 18.0, 'DASH': 0.001, 'DOT': 0.1,
        'ENJ': 14.0, 'EOS': 0.1, 'ETH': 0.01, 'EXY': 520.0,
        'GAME': 180.0, 'GGC': 9.0, 'GNT': 57.0, 'GRT': 26.0,
        'LINK': 1.05, 'LML': 800.0, 'LSK': 0.3, 'LTC': 0.001, 'LUNA': 0.02,
        'MANA': 25.0, 'MATIC': 12.0, 'MKR': 0.008,
        'NEU': 90.0, 'NPXS': 18500.0,
        'OMG': 3.1,
        'PAY': 250.0,
        'QARK': 95.0,
        'REP': 1.2,
        'SRN': 2000.0, 'SUSHI': 1.8,
        'TRX': 1.0,
        'UNI': 0.8, 'USDC': 26.0, 'USDT': 20.0,
        'XBX': 950.0, 'XIN': 5.0, 'XLM': 0.005, 'XRP': 0.1, 'XTZ': 0.1,
        'ZEC': 0.004, 'ZRX': 20.0
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
