import requests
import time


API = 'https://bitbay.net/API/Public/'


def data_request(cryptocurrency, currency):
    return requests.get(API+cryptocurrency+currency+'/orderbook.json')


def get_data(cryptocurrency, currency):
    response = data_request(cryptocurrency, currency)
    if response:
        return response.json()
    else:
        return None


def print_data(cryptocurrency, currency, limit):
    data = get_data(cryptocurrency, currency)
    if data is not None:
        print('______' + cryptocurrency + currency + '______\n')
        print('OFERTY KUPNA')
        print('-----------------------------------------')
        index = 1
        for offer in data['bids'][:limit]:
            price = str(round(offer[0] * offer[1], 3))
            print(str(index)+'. ' + str(offer[1]) + '[' + cryptocurrency + ']' + ' = ' + price + '[' + currency + ']')
            index += 1
        index = 1
        print('\nOFERTY SPRZEDAŻY')
        print('-----------------------------------------')
        for offer in data['asks'][:limit]:
            price = str(round(offer[0] * offer[1], 3))
            print(str(index) + '. ' + str(offer[1]) + '[' + cryptocurrency + ']' + " = " + price + '[' + currency + ']')
            index += 1

        print('\n')


def calculate_profit(cryptocurrency, currency, delay, limit):
    while True:
        data = get_data(cryptocurrency, currency)
        buyOffers = data['bids']
        sellOffers = data['asks']
        minimum = min(len(buyOffers), len(sellOffers))
        if limit > minimum:
            limit = minimum
        tmpBuy = 0
        tmpSell = 0
        for i in range(0, limit):
            tmpBuy += buyOffers[i][0]
            tmpSell += sellOffers[i][0]
        avBuyPrice = tmpBuy / limit
        avSellPrice = tmpSell / limit
        result = round(((avSellPrice - avBuyPrice) / avBuyPrice) * 100, 3)
        print("Zysk: " + str(result) + " %")
        time.sleep(delay)


def exercise1():
    print_data('BTC', 'USD', 20)
    print_data('LTC', 'USD', 20)
    print_data('DASH', 'USD', 20)


def exercise2():
    calculate_profit('BTC', 'USD', 5, 50)


if __name__ == '__main__':
    exercise1()
    exercise2()
