import requests


NAME = "BitBay"
BITBAY_URL = 'https://api.bitbay.net/rest/trading/orderbook-limited/'
HEADERS = {'content-type': 'application/json'}
LIMIT = 10
BITBAY_FEES = {
    "taker_fee": 0.0043,
    "transfer_fee_btc": 0.0005
}


def getOrderbookData(currency_1, currency_2):
    url = f'{BITBAY_URL}{currency_1}-{currency_2}/{LIMIT}'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getBestSellBuy(currency_1, currency_2):
    orders = getOrderbookData(currency_1, currency_2)
    if orders:
        sell = orders['sell'][0]
        buy = orders['buy'][len(orders['buy']) - 1]
        return sell, buy
    else:
        print("There was no data")
        return None


def printBestSellBuy(sell, buy, currency_1, currency_2):
    if sell and buy:
        sell_rate = sell['ra']
        sell_quantity = sell['ca']
        buy_rate = buy['ra']
        buy_quantity = buy['ca']
        print('\nOrders from BitBay:')
        print(f'Lowest sell order for {currency_1}-{currency_2}: rate: {sell_rate}, amount: {sell_quantity}')
        print(f'Highest buy order for {currency_1}-{currency_2}: rate: {buy_rate}, amount: {buy_quantity}\n')
    else:
        print("There was no data to print")
