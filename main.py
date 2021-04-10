import requests
import time

BITBAY = 'https://bitbay.net/API/Public/'
BITTREX = 'https://api.bittrex.com/api/v1.1/public/'
DELAY = 5
API_RESPONSE_OPTIONS = {BITBAY: {'code': 'code', 'info': 'message', 'success': 200},
                        BITTREX: {'code': 'success', 'info': 'message', 'success': True}
                        }
ORDERS_OPTION = {BITBAY: {'buy': 'asks', 'sell': 'bids', 'price': 0, 'amount': 1},
                 BITTREX: {'buy': 'sell', 'sell': 'buy', 'price': 'Rate', 'amount': 'Quantity'}
                 }
FEES = {BITBAY: {'takerFee': 0.001, 'transferFee': {'BTC': 0.0005}},
        BITTREX: {'takerFee': 0.0025, 'transferFee': {'BTC': 0.0005}}
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
            orders.append(offer)
    return orders


def cheapest(api, orders, onlyPrice=True):
    if len(orders) > 0:
        tmp = orders[0]
        for order in orders:
            if order[ORDERS_OPTION[api]['price']] < tmp[ORDERS_OPTION[api]['price']]:
                tmp = order
        if onlyPrice:
            return tmp[ORDERS_OPTION[api]['price']]
        else:
            return tmp
    else:
        return None


def most_expensive(api, orders, onlyPrice=True):
    if len(orders) > 0:
        tmp = orders[0]
        for order in orders:
            if order[ORDERS_OPTION[api]['price']] > tmp[ORDERS_OPTION[api]['price']]:
                tmp = order
        if onlyPrice:
            return tmp[ORDERS_OPTION[api]['price']]
        else:
            return tmp
    else:
        return None


def calculate_percentage_diff(order1, order2):
    return round(((order1 - order2) / order2) * 100, 3)


def exercise1a():
    while True:
        ordersToBuy1 = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        ordersToBuy2 = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        diff = calculate_percentage_diff(cheapest(BITBAY, ordersToBuy1), cheapest(BITTREX, ordersToBuy2))
        print('Bitbay[BUY] to Bittrex[BUY] ' + str(diff) + '%')
        time.sleep(DELAY)


def exercise1b():
    while True:
        ordersToSell1 = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        ordersToSell2 = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff = calculate_percentage_diff(most_expensive(BITBAY, ordersToSell1), most_expensive(BITTREX, ordersToSell2))
        print('Bitbay[SELL] to Bittrex[SELL] ' + str(diff) + '%')
        time.sleep(DELAY)


def exercise1c():
    while True:
        ordersToBuy = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        ordersToSell = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff1 = calculate_percentage_diff(most_expensive(BITTREX, ordersToSell), cheapest(BITBAY, ordersToBuy))
        ordersToBuy = get_orders(BITTREX, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
        ordersToSell = get_orders(BITBAY, BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
        diff2 = calculate_percentage_diff(most_expensive(BITBAY, ordersToSell), cheapest(BITTREX, ordersToBuy))
        print('Bitbay[BUY] to Bittrex[SELL] ' + str(diff1) + '%')
        print('Bittrex[BUY] to Bitbay[SELL] ' + str(diff2) + '%')
        time.sleep(DELAY)


def exercise2():
    while True:
        trades = [[BITBAY, BITTREX], [BITTREX, BITBAY]]
        for trade in trades:
            print(f'from {trade[0]} to {trade[1]}')
            ordersToBuy = get_orders(trade[0], BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[1])
            ordersToSell = get_orders(trade[1], BASE_CRYPTO, BASE_CURRENCY, ORDER_TYPES[0])
            bestBuyOrder = cheapest(trade[0], ordersToBuy, False)
            bestSellOrder = most_expensive(trade[1], ordersToSell, False)
            amount = min(bestBuyOrder[ORDERS_OPTION[trade[0]]['amount']],
                         bestSellOrder[ORDERS_OPTION[trade[1]]['amount']])
            toPay = amount * bestBuyOrder[ORDERS_OPTION[trade[0]]['price']]
            toPay *= (1 + FEES[trade[0]]['takerFee'])
            toEarn = amount * bestSellOrder[ORDERS_OPTION[trade[1]]['price']]
            toEarn -= FEES[trade[1]]['transferFee'][BASE_CRYPTO] * bestSellOrder[ORDERS_OPTION[trade[1]]['price']]
            toEarn *= (1 - FEES[trade[1]]['takerFee'])
            print('Amount: ' + str(amount) + f'[{BASE_CRYPTO}]')
            print('Profit in %: ' + str(calculate_percentage_diff(toEarn, toPay)) + '%')
            print('Profit: ' + str(round(toEarn - toPay, 3)) + f'[{BASE_CURRENCY}]\n')
        time.sleep(DELAY)
        print('\n')


if __name__ == '__main__':
    # exercise1a()
    # exercise1b()
    # exercise1c()
    exercise2()
