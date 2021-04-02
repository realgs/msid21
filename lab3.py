import requests
import time
from multiprocessing import Pool

CURRENCIES = ['ETH', 'LTC', 'BTC', 'USD']
USD = 3
BTC = 2
DEFAULT_TIMEOUT = 3
TYPES = ['buy', 'sell']
APIs = ['bittrex', 'bitbay']
API_FEES = {'bitbay': {'taker': 0.0042, 'transfer': [0.01, 0.001, 0.0005, 3]},
            'bittrex': {'taker': 0.0075}, 'transfer': [0.006, 0.01, 0.0005, 0]}
BITBAY = 1
BITTREX = 0
FUNCTIONS = ['percent_diff_buy', 'percent_diff_sell', 'percent_diff_arbitrage']
API_OPTIONS = {'bitbay': {'request': ['trades', 'orderbook', 'market', 'ticker', 'all'],
                          'path': 'https://bitbay.net/API/Public/', 'format': 'json'},
               'bittrex': {'request': ['getorderbook', 'getticker'],
                           'path': 'https://api.bittrex.com/api/v1.1/public', 'format': '&type=both'}}


def get_api_path(currency_in_nbr, currency_out_nbr, category_nbr, api_nbr):
    if 0 <= api_nbr < len(APIs) and 0 <= currency_in_nbr < len(CURRENCIES) and 0 <= currency_out_nbr < len(CURRENCIES):
        api = APIs[api_nbr]
        if api_nbr == BITTREX and 0 <= category_nbr < len(API_OPTIONS[api]['request']):
            return str('{0}/{1}?market={2}-{3}{4}'.format(API_OPTIONS[api]['path'],
                                                          API_OPTIONS[api]['request'][category_nbr],
                                                          CURRENCIES[currency_in_nbr], CURRENCIES[currency_out_nbr],
                                                          API_OPTIONS[api]['format']))
        elif api_nbr == BITBAY and 0 <= category_nbr < len(API_OPTIONS[api]['request']):
            return str('{0}{1}{2}/{3}.{4}'.format(API_OPTIONS[api]['path'], CURRENCIES[currency_out_nbr],
                                                  CURRENCIES[currency_in_nbr],
                                                  API_OPTIONS[api]['request'][category_nbr],
                                                  API_OPTIONS[api]['format']))
        else:
            return None
    return None


def get_response(path):
    if path is not None:
        resp = requests.get(path, timeout=DEFAULT_TIMEOUT)
        if 200 <= resp.status_code < 300:
            return resp
        else:
            return None
    return None


def get_best_order(currency_in_nbr, currency_out_nbr, api_nbr):
    rate_dict = {}
    if api_nbr == BITTREX:
        resp = get_response(get_api_path(currency_in_nbr, currency_out_nbr, 0, api_nbr))
        if resp is not None:
            resp_json = resp.json()
            rate_dict[TYPES[0]] = [resp_json['result']['sell'][0]['Rate'], resp_json['result']['sell'][0]['Quantity']]
            rate_dict[TYPES[1]] = [resp_json['result']['buy'][0]['Rate'], resp_json['result']['buy'][0]['Quantity']]
        return rate_dict
    elif api_nbr == BITBAY:
        resp = get_response(get_api_path(currency_in_nbr, currency_out_nbr, 1, api_nbr))
        if resp is not None:
            resp_json = resp.json()
            rate_dict[TYPES[0]] = resp_json['asks'][0]
            rate_dict[TYPES[1]] = resp_json['bids'][0]
        return rate_dict
    else:
        return None


def percent_diff_buy(currency_in_nbr, currency_out_nbr):
    if 0 <= currency_in_nbr < len(CURRENCIES) and 0 <= currency_out_nbr < len(CURRENCIES):
        rate_1 = get_best_order(currency_in_nbr, currency_out_nbr, BITTREX)['buy'][0]
        rate_2 = get_best_order(currency_in_nbr, currency_out_nbr, BITBAY)['buy'][0]
        return ((rate_2 - rate_1) / rate_1) * 100
    return None


def percent_diff_sell(currency_in_nbr, currency_out_nbr):
    if 0 <= currency_in_nbr < len(CURRENCIES) and 0 <= currency_out_nbr < len(CURRENCIES):
        rate_1 = get_best_order(currency_in_nbr, currency_out_nbr, BITTREX)['sell'][0]
        rate_2 = get_best_order(currency_in_nbr, currency_out_nbr, BITBAY)['sell'][0]
        return ((rate_2 - rate_1) / rate_1) * 100
    return None


def percent_diff_arbitrage(currency_in_nbr, currency_out_nbr, buy_api_nbr, sell_api_nbr, fees_on=False):
    if 0 <= buy_api_nbr < len(APIs) and 0 <= sell_api_nbr < len(APIs):
        if 0 <= currency_in_nbr < len(CURRENCIES) and 0 <= currency_out_nbr < len(CURRENCIES):
            offer_buy = get_best_order(currency_in_nbr, currency_out_nbr, buy_api_nbr)['buy']
            offer_sell = get_best_order(currency_in_nbr, currency_out_nbr, sell_api_nbr)['sell']
            amount = min(offer_buy[1], offer_sell[1])
            sum_pay = amount * offer_buy[0]
            sum_get = amount * offer_sell[0]
            if fees_on:
                sum_pay = sum_pay * (1 + API_FEES[APIs[buy_api_nbr]]['taker'])
                sum_get = (amount - API_FEES[APIs[buy_api_nbr]]['transfer'][currency_out_nbr]) * offer_sell[0]
                sum_get = sum_get * (1 - API_FEES[APIs[sell_api_nbr]]['taker'])
                profit = sum_get - sum_pay
                return [(1 - (sum_pay - sum_get) / sum_get) * 100, profit, amount]
            return [(1 - (sum_pay - sum_get) / sum_get) * 100]
    return None


def update(task, *args, delay=5):
    while True:
        run_and_print(task, *args)
        time.sleep(delay)


def run_and_print(task, *args):
    result = task(*args)
    if result is not None:
        if task.__name__ == FUNCTIONS[0]:
            print("Difference buy", result, "%")
        elif task.__name__ == FUNCTIONS[1]:
            print("Difference sell", result, "%")
        elif task.__name__ == FUNCTIONS[2]:
            if len(result) > 1:
                print("Arbitrage percent", result[0], "% buy in", APIs[args[2]], "sell in", APIs[args[3]],
                      "profit", result[1], CURRENCIES[args[0]], "amount", result[2], CURRENCIES[args[1]])
            else:
                print("Arbitrage percent", result[0], "% buy in", APIs[args[2]], "sell in", APIs[args[3]])


def main():
    pool = Pool()
    results = [pool.apply_async(update, [percent_diff_buy, USD, BTC]),
               pool.apply_async(update, [percent_diff_sell, USD, BTC]),
               pool.apply_async(update, [percent_diff_arbitrage, USD, BTC, BITBAY, BITTREX]),
               pool.apply_async(update, [percent_diff_arbitrage, USD, BTC, BITBAY, BITTREX, True])]
    for r in results:
        r.get()


if __name__ == '__main__':
    main()
