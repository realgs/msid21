import requests


NAME = "Bittrex"
BITTREX_URL = "https://api.bittrex.com/api/v1.1/public"
HEADERS = {'content-type': 'application/json'}
BITTREX_FEES = {
    "taker_fee": 0.0035,
    "transfer_fee_btc": 0.0005
}


def getOrderbookData(currency_1, currency_2):
    url = f'{BITTREX_URL}/getorderbook?market={currency_1}-{currency_2}&type=both'
    response = requests.request("GET", url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code, ' ', response.reason)
        return None


def getBestSellBuy(currency_1, currency_2):
    orders = getOrderbookData(currency_1, currency_2)
    if orders:
        sell = orders['result']['sell'][0]
        buy = orders['result']['buy'][0]
        return sell, buy
    else:
        print("There was no data")
        return None


def printBestSellBuy(sell, buy, currency_1, currency_2):
    if sell and buy:
        sell_rate = sell['Rate']
        sell_quantity = sell['Quantity']
        buy_rate = buy['Rate']
        buy_quantity = buy['Quantity']
        print('Orders from Bittrex:')
        print(f'Lowest sell order for {currency_1}-{currency_2}: rate: {sell_rate}, amount: {sell_quantity}')
        print(f'Highest buy order for {currency_1}-{currency_2}: rate: {buy_rate}, amount: {buy_quantity}\n')
    else:
        print("There was no data to print")
