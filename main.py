from api import Api

API = Api()
DEPTH = 15


def get_common_markets(api1, api2):
    api1_markets = API.markets(api1)
    api2_markets = API.markets(api2)
    tmp = []
    for ma in api1_markets:
        if ma in api2_markets:
            tmp.append(ma)
    return tmp


def calculate_profit(buy_api, sell_api, market):
    buy_orders = API.orders(buy_api, market, 'buy', depth=DEPTH)
    sell_orders = API.orders(sell_api, market, 'sell', depth=DEPTH)
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
    # return profit in %
    if to_Earn != 0 and to_Pay != 0:
        return (to_Earn - to_Pay) / to_Pay
    return 0


if __name__ == '__main__':
    trade_from = 'BITBAY'
    trade_to = 'BITTREX'
    trades = []
    for m in get_common_markets(trade_from, trade_to):
        trades.append({'market': m, 'profit': calculate_profit(trade_from, trade_to, m)})
    trades.sort(key=lambda x: round(x['profit'], 3), reverse=True)
    print(f'Trades from {trade_from} to {trade_to}:')
    count = 0
    for t in trades:
        count += 1
        m = t['market']
        profit = round(t['profit'], 3)
        print(f'{count}.\t{m}:\t{profit}\t%')
