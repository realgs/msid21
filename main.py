import json
import api
from tabulate import tabulate
import math

TYPE_KEYS = ['foreign_stocks', 'polish_stocks', 'cryptocurrencies', 'currencies']
APIS = {'foreign_stocks': [api.YAHOO], 'polish_stocks': [api.STOOQ], 'cryptocurrencies': [api.BITTREX, api.BITBAY],
        'currencies': [api.NBP]}
VALUE_KEYS = ['name', 'quantity', 'avg_price', 'curr']
CONFIG_FILE = 'config.json'
BASE_CURRENCY = 'PLN'
DEPTH = 25
NET = 0.81
API = api.Api()


def load_resources():
    file = open(CONFIG_FILE, 'r')
    return json.load(file)


def print_resources(resources):
    print(f'\t{VALUE_KEYS[0]}\t{VALUE_KEYS[1]}\t{VALUE_KEYS[2]}\t{VALUE_KEYS[3]}')
    count = 1
    for resource_type in TYPE_KEYS:
        for resource in resources[resource_type]:
            result = f'{count}. '
            for value in VALUE_KEYS:
                result += f'\t{resource[value]}'
            print(result)
            count += 1


def save_resources(resources):
    file = open(CONFIG_FILE, 'w')
    json.dump(resources, file, ensure_ascii=False, indent=4)


def update_resources(resource_type, name, quantity, avg_price, curr):
    old_resources = load_resources()
    new_resource = {VALUE_KEYS[0]: name, VALUE_KEYS[1]: quantity, VALUE_KEYS[2]: avg_price, VALUE_KEYS[3]: curr}
    for resource in old_resources[resource_type]:
        if resource[VALUE_KEYS[0]] == name:
            old_resources[resource_type].remove(resource)
            break
    old_resources[resource_type].append(new_resource)
    save_resources(old_resources)


def convert_currency(base, target, value):
    if base == target:
        return round(value, 4)
    elif base == BASE_CURRENCY:
        market = f'{target}-{base}'
        rate = 1 / API.last_rate(api.NBP, market)['rate']
    else:
        market = f'{base}-{target}'
        rate = API.last_rate(api.NBP, market)['rate']
    return round(value * rate, 4)


def calculate_sale_profit(sell_api, resource_name, quantity, price, currency):
    market = f'{resource_name}-{currency}'
    orders = API.orders(sell_api, market, depth=DEPTH)
    to_Pay = quantity * price
    if orders is None:
        last_rate = API.last_rate(sell_api, market)
        if last_rate is None:
            return {'abs': -math.inf, 'percent': -math.inf}
        profit = (last_rate['rate'] - price) * quantity
    else:
        to_Earn = 0
        sold_amount = 0
        orders.sort(key=lambda o: o['rate'], reverse=True)
        while len(orders) > 0 and quantity > 0:
            order = orders.pop(0)
            if order['amount'] > quantity:
                sell_amount = quantity
            else:
                sell_amount = order['amount']
            sold_amount += sell_amount
            to_Earn += sell_amount * order['rate'] * (1 - API.transaction_fee(sell_api))
            quantity -= sell_amount
        profit = to_Earn - to_Pay
    return {'abs': convert_currency(currency, BASE_CURRENCY, profit), 'percent': profit/to_Pay}


def best_sale_profit(resource_type, resource_name, quantity, price, currency):
    profits = []
    for sell_api in APIS[resource_type]:
        result = {'api': sell_api, 'profit': calculate_sale_profit(sell_api, resource_name, quantity, price, currency)}
        profits.append(result)
    profits.sort(key=lambda p: p['profit']['abs'], reverse=True)
    return profits[0]


def calculate_arbitrage(buy_api, sell_api, market, quantity):
    buy_orders = API.orders(buy_api, market, 'buy', depth=DEPTH)
    sell_orders = API.orders(sell_api, market, 'sell', depth=DEPTH)
    if buy_orders is None or sell_orders is None:
        return {'abs': -math.inf, 'percent': -math.inf}
    symbol = market.split('-')[0]
    to_Earn = 0
    to_Pay = 0
    while min(len(buy_orders), len(sell_orders)) > 0:
        buy_order = buy_orders.pop(0)
        sell_order = sell_orders.pop(0)
        # calculate arbitrage amount
        if buy_order['amount'] - API.transfer_fee(buy_api, symbol) >= sell_order['amount']:
            sell_amount = sell_order['amount']
            buy_amount = sell_order['amount'] + API.transfer_fee(buy_api, symbol)
            buy_order['amount'] = buy_order['amount'] - buy_amount
            if buy_order['amount'] > 0:
                buy_orders.insert(0, buy_order)
        elif buy_order['amount'] > API.transfer_fee(buy_api, symbol):
            sell_amount = buy_order['amount'] - API.transfer_fee(buy_api, symbol)
            buy_amount = buy_order['amount']
            sell_order['amount'] = sell_order['amount'] - sell_amount
            sell_orders.insert(0, sell_order)
        else:
            continue
        # calculate income and loss
        tmp_earn = sell_amount * sell_order['rate'] * (1 - API.transaction_fee(sell_api))
        tmp_pay = buy_amount * buy_order['rate'] * (1 + API.transaction_fee(buy_api))
        if tmp_pay > quantity:
            continue
        quantity -= tmp_pay
        # calculate profit
        if to_Earn == 0 and to_Pay == 0:
            to_Earn = tmp_earn
            to_Pay = tmp_pay
        else:
            if tmp_earn > tmp_pay:
                to_Earn += tmp_earn
                to_Pay += tmp_pay
            else:
                break
    # return profit
    if to_Earn != 0 and to_Pay != 0:
        profit = round(to_Earn - to_Pay, 5)
    else:
        profit = 0
    return {'abs': profit, 'percent': profit / to_Pay}


def best_arbitrage(resource_name, resource_quantity, cryptocurrencies, resource_type='cryptocurrencies'):
    if resource_type != 'cryptocurrencies':
        return {'apis': '---', 'market': '---', 'profit': {'abs': '---', 'percent': '---'}}
    profits = []
    buy_apis = APIS[resource_type]
    sell_apis = buy_apis
    for crypto in cryptocurrencies:
        if resource_name == crypto['name']:
            continue
        name = crypto['name']
        market = f'{name}-{resource_name}'
        for buy_api in buy_apis:
            for sell_api in sell_apis:
                if sell_api == buy_api:
                    continue
                result = {'apis': f'{buy_api}-{sell_api}',
                          'market': market,
                          'profit': calculate_arbitrage(buy_api, sell_api, market, resource_quantity)}
                profits.append(result)
    profits.sort(key=lambda p: p['profit']['abs'], reverse=True)
    return profits[0]


def calculate_net(value):
    if value < 0:
        return round(value, 4)
    return round(value * NET, 4)


def investments(resources, depth=0.1):
    depth_percent = f'{depth * 100}%'
    table = [['Nazwa', 'Ilosc', 'Cena', 'Giełda', 'Zysk', 'Zysk netto', f'Zysk {depth_percent}',
              f'Zysk {depth_percent} netto', 'Arbitraz']]
    profit = 0
    profit_net = 0
    depth_profit = 0
    depth_profit_net = 0
    for resource_type in resources.keys():
        for resource in resources[resource_type]:
            sale_profit = best_sale_profit(resource_type, resource['name'], resource['quantity'], resource['avg_price'],
                                           resource['curr'])
            depth_sale_profit = best_sale_profit(resource_type, resource['name'], resource['quantity'] * depth,
                                                 resource['avg_price'], resource['curr'])
            arbitrage_profit = best_arbitrage(resource['name'], resource['quantity'], resources[resource_type],
                                              resource_type=resource_type)
            # sum
            profit += sale_profit['profit']['abs']
            profit_net += sale_profit['profit']['abs'] * NET
            depth_profit += depth_sale_profit['profit']['abs']
            depth_profit_net += depth_sale_profit['profit']['abs'] * NET
            avg_price_pln = convert_currency(resource['curr'], BASE_CURRENCY, resource['avg_price'])
            # arbitrage_result
            if arbitrage_profit['profit']['abs'] != -math.inf:
                arb_profit = f"{arbitrage_profit['apis']}, {arbitrage_profit['market']}, "
                if arbitrage_profit['profit']['abs'] != '---':
                    arb_profit += f"{arbitrage_profit['profit']['abs']:.5f}{arbitrage_profit['market'].split('-')[1]}"
                else:
                    arb_profit += arbitrage_profit['profit']['abs']
            else:
                arb_profit = '---, ---, ---'
            # final result
            result = [resource['name'], resource['quantity'], f"{avg_price_pln}{BASE_CURRENCY}", sale_profit['api'],
                      f"{sale_profit['profit']['abs']}{BASE_CURRENCY}",
                      f"{calculate_net(sale_profit['profit']['abs'])}{BASE_CURRENCY}",
                      f"{depth_sale_profit['profit']['abs']}{BASE_CURRENCY}",
                      f"{calculate_net(depth_sale_profit['profit']['abs'])}{BASE_CURRENCY}",
                      f"{arb_profit}"]
            table.append(result)
    sum_line = ['Suma', '---', '---', '---', f"{round(profit, 4)}PLN", f"{round(profit_net, 4)}PLN",
                f"{round(depth_profit)}PLN", f"{round(depth_profit_net)}PLN", '---']
    table.append(sum_line)
    print(tabulate(table))


if __name__ == '__main__':
    # print(calculate_sale_profit(api.BITTREX, 'BTC', 0.5224, 33485.90, 'USD')['abs'])
    investments(load_resources())
