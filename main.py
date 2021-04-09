import requests
import time

BITBAY = 'https://bitbay.net/API/Public/'
BITTREX= 'https://api.bittrex.com/api/v1.1/public/'
DELAY = 5
API_RESPONSE_OPTIONS = {BITBAY: {'code': 'code', 'info': 'message', 'success': 200},
                        BITTREX: {'code': 'success', 'info': 'message', 'success': True}
                        }
ORDERS_OPTION = {BITBAY: {'buy': 'bids', 'sell': 'asks', 'price': 0},
                 BITTREX: {'buy': 'buy', 'sell': 'sell', 'price': 'Rate'}
                 }
ORDER_TYPES = ['sell', 'buy']
BASE_CURRENCY = 'USD'
BASE_CRYPTO = 'BTC'
LIMIT = 5


def data_request(api, cryptocurrency, currency):
    if api == BITBAY:
        return requests.get(api + cryptocurrency + currency + '/orderbook.json')
    elif api == BITTREX:
        return requests.get(api + 'getorderbook?market=' + currency + '-' + cryptocurrency + '&type=both')
    else:
        return None


def get_data(api, cryptocurrency, currency):
    response = data_request(api, cryptocurrency, currency)
    if response is None:
        print('unknown API')
        return None
    else:
        data = response.json()
        if API_RESPONSE_OPTIONS[api]['code'] not in data:
            return data
        elif data[API_RESPONSE_OPTIONS[api]['code']] == API_RESPONSE_OPTIONS[api]['success']:
            return data
        else:
            print(data[API_RESPONSE_OPTIONS[api]['info']])
            return None


def get_orders(api, cryptocurrency, currency, orderType, limit=LIMIT):
    data = get_data(api, cryptocurrency, currency)
    orders = []
    if data is not None:
        if 'result' in data:
            data = data['result']
        offers = data[ORDERS_OPTION[api][orderType]]
        for offer in offers[:limit]:
            orders.append(offer[ORDERS_OPTION[api]['price']])
    return orders


def cheapest(orders):
    if len(orders) > 0:
        return min(orders)
    else:
        return None


def most_expensive(orders):
    if len(orders) > 0:
        return max(orders)
    else:
        return None


def calculate_percentage_difference(order1, order2):
    return round(((order1 - order2) / order2) * 100, 3)


def exercise1a():
    while True:
        buyOrders1 = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        buyOrders2 = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        diff = calculate_percentage_difference(most_expensive(buyOrders1), most_expensive(buyOrders2))
        print('Bitbay[BUY] to Bittrex[BUY] ' + str(diff) + '%')
        time.sleep(DELAY)


def exercise1b():
    while True:
        sellOrders1 = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        sellOrders2 = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff = calculate_percentage_difference(cheapest(sellOrders1), cheapest(sellOrders2))
        print('Bitbay[SELL] to Bittrex[SELL] ' + str(diff) + '%')
        time.sleep(DELAY)


def exercise1c():
    while True:
        buyOrders = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        sellOrders = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff1 = calculate_percentage_difference(cheapest(buyOrders), most_expensive(sellOrders))
        buyOrders = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        sellOrders = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff2 = calculate_percentage_difference(cheapest(buyOrders), most_expensive(sellOrders))
        print('Bitbay[BUY] to Bittrex[SELL] ' + str(diff1) + '%')
        print('Bittrex[BUY] to Bitbay[SELL] ' + str(diff2) + '%')
        time.sleep(DELAY)


if __name__ == '__main__':
    exercise1c()
