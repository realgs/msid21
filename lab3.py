import requests
import time

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
PATH_BITBAY = 'https://bitbay.net/API/Public/'
BITBAY_REQUEST_CATEGORY = ['trades', 'orderbook', 'market', 'ticker', 'all']
DEFAULT_FORMAT = 'json'
PATH_BITTREX = 'https://api.bittrex.com/api/v1.1/public'
BITTREX_REQUEST_CATEGORY = ['getorderbook', 'getticker']
BITTREX_FORMAT = '&type=both'


def get_api_path(currency_in_nbr, currency_out_nbr, category_nbr, api_nbr):
    if 0 <= api_nbr < len(APIs) and 0 <= currency_in_nbr < len(CURRENCIES) and 0 <= currency_out_nbr < len(CURRENCIES):
        if api_nbr == 0 and 0 <= category_nbr < len(BITTREX_REQUEST_CATEGORY):
            return str('{0}/{1}?market={2}-{3}{4}'.format(PATH_BITTREX, BITTREX_REQUEST_CATEGORY[category_nbr],
                                                          CURRENCIES[currency_in_nbr], CURRENCIES[currency_out_nbr],
                                                          BITTREX_FORMAT))
        elif api_nbr == 1 and 0 <= category_nbr < len(BITBAY_REQUEST_CATEGORY):
            return str('{0}{1}{2}/{3}.{4}'.format(PATH_BITBAY, CURRENCIES[currency_out_nbr],
                                                  CURRENCIES[currency_in_nbr], BITBAY_REQUEST_CATEGORY[category_nbr],
                                                  DEFAULT_FORMAT))
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
                print(profit, amount)
            return (1 - (sum_pay - sum_get) / sum_get) * 100
    return None


def update_profit(cryptocurrency, delay, limit=50):
    while True:
        # print("Profit for", cryptocurrency, calculate_profit(cryptocurrency, limit)*100, "%")
        time.sleep(delay)


def main():
    print(percent_diff_buy(USD, BTC))
    print(percent_diff_sell(USD, BTC))
    print(percent_diff_arbitrage(USD, BTC, BITBAY, BITTREX))
    print(percent_diff_arbitrage(USD, BTC, BITBAY, BITTREX, True))


if __name__ == '__main__':
    main()
