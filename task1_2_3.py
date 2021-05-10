from enum import Enum
from multiprocessing import Pool
import time
import requests

BITTREX = 'BITTREX'
BITBAY = 'BITBAY'
TAKER = 'TAKER'
TRANSFER = 'TRANSFER'
ORDERBOOK = 'ORDERBOOK'
MARKETS = 'MARKETS'
BUY = 'BUY'
QUANTITY = 'QUANTITY'
RATE = 'RATE'
SELL = 'SELL'
DATA_CONST = {BITBAY: {SELL: 'bids', BUY: 'asks', QUANTITY: 1, RATE: 0, MARKETS: 'items'},
              BITTREX: {SELL: 'bid', BUY: 'ask', QUANTITY: 'quantity', RATE: 'rate', MARKETS: 'symbol'}}

ADDRESSES = {BITBAY: {MARKETS: 'https://api.bitbay.net/rest/trading/ticker',
                      ORDERBOOK: 'https://bitbay.net/API/Public/{}/orderbook.json'},
             BITTREX: {MARKETS: 'https://api.bittrex.com/v3/markets',
                       ORDERBOOK: 'https://api.bittrex.com/v3/markets/{}/orderbook?depth=25'}}

FEES = {'BITBAY': {'TAKER': 0.0042, 'TRANSFER': {'AAVE': 0.23, 'BAT': 29, 'BSV': 0.003, 'BTC': 0.0005, 'COMP': 0.025,
                                                 'DAI': 19, 'DOT': 0.1, 'EOS': 0.1, 'ETH': 0.01, 'EUR': 3, 'GAME': 279,
                                                 'GRT': 11, 'LINK': 1.85, 'LSK': 0.3,
                                                 'LTC': 0.001, 'LUNA': 0.02, 'MANA': 27, 'MKR': 0.014, 'NPXS': 22400,
                                                 'OMG': 3.5, 'PAY': 278, 'SRN': 2905, 'TRX': 1,
                                                 'UNI': 0.7, 'USD': 3, 'USDC': 75.5, 'USDT': 37, 'XLM': 0.005,
                                                 'XRP': 0.1, 'XTZ': 0.1, 'ZRX': 16}},
        'BITTREX': {'TAKER': 0.0075, 'TRANSFER': {'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05,
                                                  'DAI': 42, 'DOT': 0.5, 'EOS': 0.1, 'ETH': 0.006, 'EUR': 0,
                                                  'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1,
                                                  'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29, 'MKR': 0.0095, 'NPXS': 10967,
                                                  'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003,
                                                  'UNI': 1, 'USD': 0, 'USDC': 42, 'USDT': 42, 'XLM': 0.05, 'XRP': 1,
                                                  'XTZ': 0.25, 'ZRX': 25}}}


class ArbitrageCode(Enum):
    BITTREX_BITBAY = 0
    BITBAY_BITTREX = 1


def get_json(api, address_type, currencies=None):
    try:
        if address_type == ORDERBOOK and currencies is not None:
            response = requests.get(ADDRESSES[api][address_type].format(currencies))
        elif address_type == MARKETS:
            response = requests.get(ADDRESSES[api][address_type])
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Connection to api failed")
        return None


def get_data(response, sell_or_buy, quantity_or_rate, offer_number=0):
    return response[sell_or_buy][offer_number][quantity_or_rate]


def get_percentage_difference(first, second):
    return (1 - (first - second) / second) * 100


def change_format(currencies):
    result = currencies.split("-")
    return result[0] + result[1]


def get_sum(earning_list):
    quantity_sum = 0
    earn_sum = 0
    for earn in earning_list:
        if earn["earn"] > 0:
            quantity_sum += earn["quantity"]
            earn_sum += earn["earn"]
    return {"quantity": quantity_sum, "earn": earn_sum}


def print_arbitrage(currencies, arbitrage_code, with_fees=True):
    if arbitrage_code.value == ArbitrageCode.BITTREX_BITBAY.value:
        print("Arbitrage " + currencies + ": buy on bittrex, sell on bitbay")
    elif arbitrage_code.value == ArbitrageCode.BITBAY_BITTREX.value:
        print("Arbitrage " + currencies + ": buy on bitbay, sell on bittrex")
    print(get_arbitrage_list(currencies, arbitrage_code, with_fees))


def get_arbitrage_list(currencies, arbitrage_code, with_fees, response_bitbay=None, response_bittrex=None):
    if response_bittrex is None and response_bitbay is None:
        response_bitbay = get_json(BITBAY, ORDERBOOK, change_format(currencies))
        response_bittrex = get_json(BITTREX, ORDERBOOK, currencies)
    if response_bittrex is not None and response_bitbay is not None:
        earning_list = get_arbitrage_rec(currencies, response_bitbay, response_bittrex,
                                         arbitrage_code.value, with_fees, 0, 0, 0)
        if len(earning_list) > 1:
            earning_list = [get_sum(earning_list)] + earning_list
        return earning_list
    else:
        print("data not found", "\n")
        return None


def get_arbitrage_rec(currencies, response_bitbay, response_bittrex, arbitrage_code,
                      with_fees, buy_offer_number, sell_offer_number, in_quantity):
    earning_list = []
    transaction_quantity, rest_quantity, payment, profit = \
        get_arbitrage(arbitrage_code, currencies, response_bitbay,
                      response_bittrex, buy_offer_number, sell_offer_number, in_quantity, with_fees)

    earning = profit - payment
    earning_list.append({"quantity": transaction_quantity, "earn": earning,
                         "buy_num": buy_offer_number, "sell_num": sell_offer_number})
    if earning > 0:
        time.sleep(0.5)
        if rest_quantity > 0:
            earning_list += get_arbitrage_rec(currencies, response_bitbay, response_bittrex, arbitrage_code,
                                              with_fees, buy_offer_number,
                                              sell_offer_number + 1, rest_quantity)
        elif rest_quantity < 0:
            earning_list += get_arbitrage_rec(currencies, response_bitbay, response_bittrex, arbitrage_code,
                                              with_fees, buy_offer_number + 1,
                                              sell_offer_number, rest_quantity)
        else:
            earning_list += get_arbitrage_rec(currencies, response_bitbay, response_bittrex, arbitrage_code,
                                              with_fees, buy_offer_number + 1,
                                              sell_offer_number + 1, 0)
    return earning_list


def get_arbitrage(arbitrage_code, currencies, response_bitbay, response_bittrex, buy_offer_number,
                  sell_offer_number, input_quantity, with_fees):
    if arbitrage_code == 0:
        fee_source = BITTREX
        buy_quantity = float(
            get_data(response_bittrex, DATA_CONST[BITTREX][BUY], DATA_CONST[BITTREX][QUANTITY], buy_offer_number))
        buy_rate = float(
            get_data(response_bittrex, DATA_CONST[BITTREX][BUY], DATA_CONST[BITTREX][RATE], buy_offer_number))
        sell_quantity = get_data(response_bitbay, DATA_CONST[BITBAY][SELL], DATA_CONST[BITBAY][QUANTITY],
                                 sell_offer_number)
        sell_rate = get_data(response_bitbay, DATA_CONST[BITBAY][SELL], DATA_CONST[BITBAY][RATE], sell_offer_number)
    elif arbitrage_code == 1:
        fee_source = BITBAY
        sell_quantity = float(
            get_data(response_bittrex, DATA_CONST[BITTREX][SELL], DATA_CONST[BITTREX][QUANTITY], sell_offer_number))
        sell_rate = float(
            get_data(response_bittrex, DATA_CONST[BITTREX][SELL], DATA_CONST[BITTREX][RATE], sell_offer_number))
        buy_quantity = get_data(response_bitbay, DATA_CONST[BITBAY][BUY], DATA_CONST[BITBAY][QUANTITY],
                                buy_offer_number)
        buy_rate = get_data(response_bitbay, DATA_CONST[BITBAY][BUY], DATA_CONST[BITBAY][RATE], buy_offer_number)
    else:
        print("invalid arbitrage_code")
        return None

    if input_quantity > 0:
        buy_quantity = input_quantity
    elif input_quantity < 0:
        sell_quantity = (-1) * input_quantity

    transaction_quantity = min(buy_quantity, sell_quantity)
    rest_quantity = buy_quantity - sell_quantity

    payment = get_payment(buy_rate, transaction_quantity, FEES[fee_source][TAKER],
                          with_fees)
    profit = get_profit(sell_rate, transaction_quantity, FEES[fee_source][TAKER],
                        FEES[fee_source][TRANSFER][currencies.split("-")[0]], with_fees)

    return transaction_quantity, rest_quantity, payment, profit


def get_payment(buy_rate, buy_quantity, buy_taker, with_fees):
    if with_fees:
        payment = buy_rate * buy_quantity * (1 + buy_taker)
    else:
        payment = buy_rate * buy_quantity
    return payment


def get_profit(sell_rate, sell_quantity, sell_taker, transfer_fee, with_fees):
    if with_fees:
        profit = sell_rate * (sell_quantity - transfer_fee) * (1 - sell_taker)
    else:
        profit = sell_rate * sell_quantity
    return profit


def get_arbitrage_for_markets(markets_list, with_fees):
    markets_dict_bittrex_bitbay = {}
    markets_dict_bitbay_bittrex = {}
    arbitrages_bitbay_bittrex = {}
    arbitrages_bittrex_bitbay = {}
    with Pool(processes=4) as pool:
        for market in markets_list:
            response_bitbay = get_json(BITBAY, ORDERBOOK, change_format(market))
            response_bittrex = get_json(BITTREX, ORDERBOOK, market)
            arbitrages_bitbay_bittrex[market] = pool.apply_async(
                get_arbitrage_list, args=[market, ArbitrageCode.BITTREX_BITBAY, with_fees,
                                          response_bitbay, response_bittrex])
            arbitrages_bittrex_bitbay[market] = pool.apply_async(
                get_arbitrage_list, args=[market, ArbitrageCode.BITBAY_BITTREX, with_fees,
                                          response_bitbay, response_bittrex])

        for market in markets_list:
            markets_dict_bittrex_bitbay[market] = arbitrages_bitbay_bittrex[market].get()
            markets_dict_bitbay_bittrex[market] = arbitrages_bittrex_bitbay[market].get()

    return markets_dict_bittrex_bitbay, markets_dict_bitbay_bittrex


def print_updating_markets(delay=5, with_fees=True):
    markets = get_common_markets()
    while True:
        print_sorted_arbitrage_for_markets(markets, with_fees)
        time.sleep(delay)


def get_common_markets():
    response_bittrex = get_json(BITTREX, MARKETS)
    response_bitbay = get_json(BITBAY, MARKETS)
    markets_list_bittrex = []
    if response_bittrex is not None and response_bitbay is not None:
        for markets in response_bittrex:
            markets_list_bittrex.append(markets[DATA_CONST[BITTREX][MARKETS]])
        markets_list_bitbay = list(response_bitbay[DATA_CONST[BITBAY][MARKETS]].keys())
        return list(set(markets_list_bittrex).intersection(markets_list_bitbay))


def print_sorted_arbitrage_for_markets(markets_list, with_fees):
    markets_dict_1, markets_dict_2 = get_arbitrage_for_markets(markets_list, with_fees)
    print("Arbitrage buy on bittrex, sell on bitbay")
    print_key_in_line(
        {k: v for k, v in sorted(markets_dict_1.items(), key=lambda item: item[1][0]['earn'], reverse=True)})
    print("Arbitrage buy on bitbay, sell on bittrex")
    print_key_in_line(
        {k: v for k, v in sorted(markets_dict_2.items(), key=lambda item: item[1][0]['earn'], reverse=True)})


def print_key_in_line(markets_dict):
    for market in list(markets_dict.keys()):
        print(market, markets_dict[market])


def main():
    print_arbitrage('TRX-EUR', ArbitrageCode.BITTREX_BITBAY, True)
    print_arbitrage('TRX-EUR', ArbitrageCode.BITBAY_BITTREX, True)
    print(get_common_markets())
    print_sorted_arbitrage_for_markets(get_common_markets(), True)


if __name__ == '__main__':
    main()
