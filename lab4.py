import requests
from multiprocessing import Pool


AMOUNT = 1
RATE = 0
DEFAULT_TIMEOUT = 3
TYPES = ['buy', 'sell']
APIs = ['bittrex', 'bitbay']
BITTREX_BUY = 'bid'
BITTREX_SELL = 'ask'
BITBAY_BUY = 'bids'
BITBAY_SELL = 'asks'
API_FEES = {'bitbay': {'taker': 0.0042,
                       'transfer': {'ETH': 0.01, 'LTC': 0.001, 'BTC': 0.0005, 'USD': 3,
                                    'UNI': 0.7, 'EUR': 3, 'USDC': 75.5, 'DAI': 19, 'TRX': 1,
                                    'LSK': 0.3, 'USDT': 37, 'BSV': 0.003,
                                    'DOT': 0.1, 'NPXS': 22400, 'OMG': 3.5, 'PAY': 278, 'LINK': 1.85,
                                    'MKR': 0.014, 'SRN': 2905,
                                    'AAVE': 0.23, 'EOS': 0.1, 'LUNA': 0.02, 'MANA': 27, 'BAT': 29,
                                    'ZRX': 16, 'XLM': 0.005, 'GAME': 279,
                                    'GRT': 11, 'XRP': 0.1, 'COMP': 0.025, 'XTZ': 0.1}},
            'bittrex': {'taker': 0.0075,
                        'transfer': {'ETH': 0.006, 'LTC': 0.01, 'BTC': 0.0005, 'USD': 0,
                                     'UNI': 1, 'EUR': 0, 'USDC': 42, 'DAI': 42, 'TRX': 0.003,
                                     'LSK': 0.1, 'USDT': 42, 'BSV': 0.001,
                                     'DOT': 0.5, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'LINK': 1.15,
                                     'MKR': 0.0095, 'SRN': 1567,
                                     'AAVE': 0.4, 'EOS': 0.1, 'LUNA': 2.2, 'MANA': 29, 'BAT': 35,
                                     'ZRX': 25, 'XLM': 0.05, 'GAME': 133,
                                     'GRT': 0, 'XRP': 1, 'COMP': 0.05, 'XTZ': 0.25}}}
BITBAY = 'bitbay'
BITTREX = 'bittrex'
ORDERBOOK = 0
API_OPTIONS = {'bitbay': {'request': ['orderbook', 'market', 'ticker', 'all'],
                          'path': 'https://bitbay.net/API/Public/', 'format': 'json',
                          'markets_path': 'https://api.bitbay.net/rest/trading/ticker',
                          'market_currencies': 'items'},
               'bittrex': {'request': ['orderbook', 'ticker'],
                           'path': 'https://api.bittrex.com/v3/markets', 'format': 'depth=25',
                           'markets_path': 'https://api.bittrex.com/v3/markets',
                           'market_currencies': 'symbol'}}

TRANSACTIONS = "transactions"
PROFIT = "profit"


class ApiResponse:
    def __init__(self, currency_in, currency_out, api):
        self.__currency_in = currency_in
        self.__currency_out = currency_out
        self.__api = api
        resp = get_response(get_api_path(currency_in, currency_out, ORDERBOOK, api))
        if resp is not None:
            self.__resp_json = resp.json()
        else:
            self.__resp_json = None

    @property
    def get_currency_in(self):
        return self.__currency_in

    @property
    def get_currency_out(self):
        return self.__currency_out

    @property
    def get_api(self):
        return self.__api

    @property
    def get_offer_number(self):
        if self.__api == BITTREX:
            return min(len(self.__resp_json[BITTREX_SELL]),
                       len(self.__resp_json[BITTREX_BUY]))
        elif self.__api == BITBAY:
            return min(len(self.__resp_json[BITBAY_SELL]),
                       len(self.__resp_json[BITBAY_BUY]))

    def get_offer(self, offer_nbr):
        if offer_nbr < 0 or self.__resp_json is None or offer_nbr >= self.get_offer_number:
            return None
        rate_dict = {}
        if self.__api == BITTREX:
            rate_dict[TYPES[0]] = [float(self.__resp_json[BITTREX_SELL][offer_nbr]['rate']),
                                   float(self.__resp_json[BITTREX_SELL][offer_nbr]['quantity'])]
            rate_dict[TYPES[1]] = [float(self.__resp_json[BITTREX_BUY][offer_nbr]['rate']),
                                   float(self.__resp_json[BITTREX_BUY][offer_nbr]['quantity'])]
            return rate_dict
        elif self.__api == BITBAY:
            rate_dict[TYPES[0]] = self.__resp_json[BITBAY_SELL][offer_nbr]
            rate_dict[TYPES[1]] = self.__resp_json[BITBAY_BUY][offer_nbr]
            return rate_dict


def get_api_path(currency_in, currency_out, category_nbr, api):
    if api in APIs:
        if api == BITTREX and 0 <= category_nbr < len(API_OPTIONS[api]['request']):
            return str('{0}/{1}-{2}/{3}?{4}'.format(API_OPTIONS[api]['path'],
                                                    currency_in, currency_out,
                                                    API_OPTIONS[api]['request'][category_nbr],
                                                    API_OPTIONS[api]['format']))
        elif api == BITBAY and 0 <= category_nbr < len(API_OPTIONS[api]['request']):
            return str('{0}{1}{2}/{3}.{4}'.format(API_OPTIONS[api]['path'], currency_in,
                                                  currency_out,
                                                  API_OPTIONS[api]['request'][category_nbr],
                                                  API_OPTIONS[api]['format']))
    return None


def get_response(path):
    if path is not None:
        resp = requests.get(path, timeout=DEFAULT_TIMEOUT)
        if 200 <= resp.status_code < 300:
            return resp
    return None


def get_common_markets(api1, api2):
    if api1 in APIs and api2 in APIs:
        xs = get_markets(api1)
        ys = get_markets(api2)
        if xs is not None and ys is not None:
            return list(set(xs).intersection(ys))


def get_markets(api):
    if api in APIs:
        resp = get_response(API_OPTIONS[api]['markets_path'])
        if resp:
            resp_json = resp.json()
            if api == BITBAY:
                return get_currencies(resp_json[API_OPTIONS[api]['market_currencies']], BITBAY)
            elif api == BITTREX:
                return get_currencies(resp_json, BITTREX)


def get_currencies(response, api):
    if response is not None and api in APIs:
        currencies = []
        for item in response:
            if api == BITTREX:
                item = item[API_OPTIONS[api]['market_currencies']]
            curr = item.split("-")
            if curr not in currencies:
                currencies.append((curr[0], curr[1]))
        return currencies


def count_percent_diff(arg1, arg2):
    return ((arg2 - arg1) / arg1) * 100


def count_arbitrage(currency_in, currency_out, buy_api, sell_api, fees_on=False):
    if buy_api in APIs and sell_api in APIs:
        resp_buy = ApiResponse(currency_in, currency_out, buy_api)
        resp_sell = ApiResponse(currency_in, currency_out, sell_api)
        buy_taker = API_FEES[buy_api]['taker']
        sell_taker = API_FEES[sell_api]['taker']
        transfer_fee = API_FEES[buy_api]['transfer'][currency_out]
        positive_profit = True
        buy_offer_nbr = 0
        sell_offer_nbr = 0
        best_transaction = None
        max_profit = 0
        while positive_profit:
            transaction_deep = count_arbitrage_multi_offer_profit(resp_buy,
                                                                  resp_sell, buy_offer_nbr, sell_offer_nbr,
                                                                  buy_taker, sell_taker, transfer_fee, fees_on)
            if transaction_deep[PROFIT] > 0:
                if best_transaction:
                    if transaction_deep[PROFIT] > max_profit:
                        best_transaction = transaction_deep
                        max_profit = best_transaction[PROFIT]
                else:
                    best_transaction = transaction_deep
                    max_profit = best_transaction[PROFIT]
            else:
                positive_profit = False
                if best_transaction is None:
                    best_transaction = transaction_deep
            if resp_buy.get_offer_number - 2 > buy_offer_nbr:
                buy_offer_nbr += 1
            else:
                positive_profit = False
        return best_transaction


def count_arbitrage_multi_offer_profit(resp_buy, resp_sell, offer_buy_nbr,
                                       offer_sell_nbr, buy_taker, sell_taker, transfer_fee, fees_on=False):
    offer_buy = resp_buy.get_offer(offer_buy_nbr)['buy']
    offer_sell = resp_sell.get_offer(offer_sell_nbr)['sell']
    profit_all = 0
    amount_all = 0
    sum_pay = 0
    transactions = []
    amount = min(offer_buy[AMOUNT], offer_sell[AMOUNT])
    profitable = True
    while profitable:
        transaction = count_arbitrage_one_offer_profit(offer_buy, offer_sell, buy_taker, sell_taker, transfer_fee,
                                                       amount, fees_on)
        profit = transaction['profit']
        if profit > 0:
            profit_all += profit
            sum_pay += transaction['sum_pay']
            amount_all += amount
            transactions.append({'offer_buy': offer_buy_nbr, 'offer_sell': offer_sell_nbr, 'amount': amount})
            if offer_buy[AMOUNT] > amount_all and resp_sell.get_offer_number - 2 > offer_sell_nbr:
                offer_sell_nbr += 1
                offer_sell = resp_sell.get_offer(offer_sell_nbr)['sell']
                amount = min(offer_buy[AMOUNT] - amount_all, offer_sell[AMOUNT])
            elif offer_sell[AMOUNT] > amount_all and resp_buy.get_offer_number - 2 > offer_buy_nbr:
                offer_buy_nbr += 1
                offer_buy = resp_buy.get_offer(offer_buy_nbr)['buy']
                amount = min(offer_buy[AMOUNT], offer_sell[AMOUNT] - amount_all)
            else:
                profitable = False
        else:
            profitable = False
            transactions.append({'offer_buy': offer_buy_nbr, 'offer_sell': offer_sell_nbr, 'amount': amount})
            profit_all += profit
            sum_pay += transaction['sum_pay']
            amount_all += amount
    return {"transactions": transactions, "profit": profit_all, "amount": amount_all,
            "percent": count_percent_diff(sum_pay, profit_all + sum_pay),
            "currencies": (resp_buy.get_currency_in, resp_buy.get_currency_out)}


def count_arbitrage_one_offer_profit(offer_buy, offer_sell, buy_taker, sell_taker, transfer_fee, amount, fees_on=False):
    sum_pay = amount * offer_buy[RATE]
    sum_get = amount * offer_sell[RATE]
    if fees_on:
        sum_pay = sum_pay * (1 + buy_taker)
        sum_get = (amount - transfer_fee) * offer_sell[RATE]
        sum_get = sum_get * (1 - sell_taker)
    profit = sum_get - sum_pay
    return {'percent': count_percent_diff(sum_pay, sum_get), 'profit': profit, 'amount': amount,
            'sum_pay': sum_pay}


def get_markets_ranking(markets, buy_api, sell_api):
    with Pool(processes=4) as pool:
        results = []
        ranking = {}
        for nbr in range(len(markets)):
            results.append(pool.apply_async(count_arbitrage,
                                            args=[markets[nbr][0], markets[nbr][1], buy_api, sell_api, True]))
        for r in results:
            transaction = r.get()
            if transaction['currencies'] not in ranking:
                ranking[transaction['currencies']] = {'transactions': transaction['transactions'],
                                                      'profit': transaction['profit'],
                                                      'amount': transaction['amount'],
                                                      'percent profit': transaction['percent']}
        sorted_dict = {k: v for k, v in sorted(ranking.items(),
                                               key=lambda item: item[1]['percent profit'], reverse=True)}
        return sorted_dict


def print_markets_ranking(markets_ranking):
    for pair in markets_ranking:
        print('Buy {0} Sell {1}\t {2}'.format(pair[0], pair[1], markets_ranking[pair]))


if __name__ == '__main__':
    market = get_common_markets(BITTREX, BITBAY)
    print(market)
    print("BITBAY BITTREX\n")
    print_markets_ranking(get_markets_ranking(market, BITBAY, BITTREX))
    print("\nBITTREX BITBAY\n")
    print_markets_ranking(get_markets_ranking(market, BITTREX, BITBAY))
    print("\nTask2\n")
    print_markets_ranking(get_markets_ranking(market[:3], BITBAY, BITTREX))
