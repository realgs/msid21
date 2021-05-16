import requests


NAME = "Bittrex"
BITTREX_URL = "https://api.bittrex.com/api/v1.1/public"
BITTREX_URL_MARKETS = "https://api.bittrex.com/v3/markets"
HEADERS = {'content-type': 'application/json'}
LIMIT = 50
BITTREX_FEES = {
    "taker_fee": 0.0035,
    "transfer_fee": {
        'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5, 'EOS': 0.1,
        'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29,
        'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42,
        'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25
    }
}


def createMarketsList():
    markets_data = getMarketsData()
    markets = []
    for i in range(0, len(markets_data)):
        markets_symbols = markets_data[i]['symbol']
        markets.append(markets_symbols)
    return markets


def getMarketsData():
    url = BITTREX_URL_MARKETS
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getOrderbookData(currency_1, currency_2):
    url = f'{BITTREX_URL}/getorderbook?market={currency_1}-{currency_2}&type=both'
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
        if len(orders['result']['sell']) < limit or len(orders['result']['buy']) < limit:
            limit = min(len(orders['result']['sell']), len(orders['result']['buy']))
        for i in range(0, limit):
            sell = orders['result']['sell'][i]
            buy = orders['result']['buy'][i]
            sell_buy = sell, buy
            best_sell_buy_list.append(sell_buy)
        return best_sell_buy_list
    else:
        print("There was no data!")
        return None


def printBestSellBuy(best_sell_buy_list, currency_1, currency_2):
    if best_sell_buy_list:
        print('\nOrders from Bittrex:')
        number = 1
        for element in best_sell_buy_list:
            sell_rate = element[0]['Rate']
            sell_quantity = element[0]['Quantity']
            buy_rate = element[1]['Rate']
            buy_quantity = element[1]['Quantity']
            print(f'Sell order no.{number} for {currency_1}-{currency_2}: rate: {sell_rate}, amount: {sell_quantity}')
            print(f'Buy order no.{number} for {currency_1}-{currency_2}: rate: {buy_rate}, amount: {buy_quantity}\n')
            number += 1
        else:
            print("There was no data to print")
