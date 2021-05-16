import requests


NAME = "Bittrex"
BITTREX_URL = "https://api.bittrex.com/api/v1.1/public"
BITTREX_URL_MARKETS = "https://api.bittrex.com/v3/markets"
HEADERS = {'content-type': 'application/json'}
LIMIT = 50
BITTREX_FEES = {
    "taker_fee": 0.0035,
    "transfer_fee_btc": 0.0005
}


def createMarketsList():
    markets_data = getMarketsData()
    markets = []
    for i in range(0, len(markets_data)):
        markets_symbols = markets_data[i]['symbol']
        markets.append(markets_symbols)
    return markets


def getMarketsData():
    #markets_list = []
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
    best_sell_buy_list = []
    orders = getOrderbookData(currency_1, currency_2)
    if orders:
        for i in range(0, LIMIT):
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


if __name__ == "__main__":
    #print(getOrderbookData("USD", "BTC"))
    #print(getBestSellBuy("USD", "BTC"))
    #markets_list = createMarketsList()
    #print(markets_list)
    #printBestSellBuy(getBestSellBuy("USD", "BTC"), "USD", "BTC")
    print(createMarketsList())