import requests
import time
import Apis as ap


APIS = ap.Apis()
SINGLE_OFFER = 1
DEF_NO_OF_OFFERS = 10
SLEEP_TIME = 5


def get_response(url):
    api_response = requests.get(url)
    if 200 <= api_response.status_code <= 299:
        return api_response.json()
    else:
        print("Could not connect to API.", api_response.reason)
        return None


def get_offers(api_name, no_of_offers, crypto_currency, base_currency):
    if api_name == APIS.bitbay.name:
        all_offers = get_response(APIS.bitbay.url.format(crypto_currency, base_currency))
        if all_offers is not None:
            return {'bids': (all_offers['bids'][:no_of_offers]), 'asks': (all_offers['asks'][:no_of_offers])}
    else:
        all_offers = get_response(APIS.bittrex.url.format(base_currency, crypto_currency))
        if all_offers is not None:
            tmp = {'bids': [], 'asks': []}
            for i in range(no_of_offers):
                if i < len(all_offers['result']['buy']) and i < len(all_offers['result']['sell']):
                    bids_list = list(all_offers['result']['buy'][i].values())
                    bids_list.reverse()
                    asks_list = list(all_offers['result']['sell'][i].values())
                    asks_list.reverse()
                    tmp['bids'].append(bids_list)
                    tmp['asks'].append(asks_list)
            return tmp


def get_markets(api_name):
    if api_name == APIS.bitbay.name:
        all_markets = get_response(APIS.bitbay.markets)
        if all_markets is not None:
            tmp = []
            for key in all_markets['items'].keys():
                tmp.append(key)
            return tmp
    else:
        all_markets = get_response(APIS.bittrex.markets)
        if all_markets is not None:
            tmp = []
            for dict_ in all_markets:
                tmp.append(dict_['symbol'])
            return tmp


def get_common_markets(market_1, market_2):
    common_markets = []
    for market in market_1:
        if market in market_2:
            common_markets.append(market)
    return common_markets


def include_fees(api_name, fee_name, rate, crypto_currency):
    if fee_name == "taker_fee":
        if api_name == APIS.bitbay.name:
            return rate * (1 + APIS.bitbay.taker_fee)
        else:
            return rate * (1 + APIS.bittrex.taker_fee)
    else:
        if api_name == APIS.bitbay.name:
            return rate - APIS.bitbay.transfer_fees[crypto_currency]
        else:
            return rate - APIS.bittrex.transfer_fees[crypto_currency]


def get_initial_profit(api_name_1, api_name_2, offer_buy, offer_sell):
    amount = offer_buy[1]
    spent = include_fees(api_name_1, "taker", offer_buy[0], "BTC") * amount
    earned = include_fees(api_name_2, "transfer", offer_sell[0], "BTC") * amount
    return earned - spent


def get_arbitrage_info(api_name_1, api_name_2, crypto_currency, base_currency):
    offers_api_1 = get_offers(api_name_1, DEF_NO_OF_OFFERS, crypto_currency, base_currency)
    offers_api_2 = get_offers(api_name_2, DEF_NO_OF_OFFERS, crypto_currency, base_currency)
    initial_profit_in_base_currency = get_initial_profit(api_name_1, api_name_2,
                                                         offers_api_1['asks'][0], offers_api_2['bids'][0])
    if initial_profit_in_base_currency < 0:
        return initial_profit_in_base_currency
    i = 0
    j = 0
    profit_in_base_currency = 0
    while profit_in_base_currency > 0 and i < len(offers_api_1['asks']) and j < len(offers_api_2['bids']):
        amount = min(offers_api_1['asks'][i][1], offers_api_2['bids'][i][1])
        buy_rate = include_fees(api_name_1, "taker", offers_api_1['asks'][i][0], crypto_currency)
        sell_rate = include_fees(api_name_2, "transfer", offers_api_2['bids'][j][0], crypto_currency)
        profit_in_base_currency += (buy_rate - sell_rate) * amount
        if offers_api_1['asks'][i][1] == offers_api_2['bids'][i][1]:
            i += 1
            j += 1
        if offers_api_1['asks'][i][1] < offers_api_2['bids'][i][1]:
            j += 1
            offers_api_2['bids'][i][1] = offers_api_2['bids'][i][1] - offers_api_1['asks'][i][1]
        if offers_api_1['asks'][i][1] > offers_api_2['bids'][i][1]:
            i += 1
            offers_api_1['asks'][i][1] = offers_api_1['asks'][i][1] - offers_api_2['bids'][i][1]
    return profit_in_base_currency


def print_ex1(api_name_1, api_name_2):
    common_markets = get_common_markets(get_markets(api_name_1), get_markets(api_name_2))
    print("----EXERCISE 1:")
    print(f'\tCommon markets for {api_name_1} and {api_name_2}:')
    for i in range(1, len(common_markets)):
        print(f'\t\t{common_markets[i-1]}', end=" ")
        if i % 10 == 0 and not i == len(common_markets) - 1:
            print()
    print()


def print_ex2(api_name_1, api_name_2):
    print("----EXERCISE 2:")
    example_currencies = ["BTC-USD", "BTC-EUR", "OMG-USD"]
    while True:
        print(f'\tBuy at {api_name_1}, sell at {api_name_2}')
        for currency in example_currencies:
            currency = currency.split("-")
            print(f'\t\tBuy {currency[0]} for {currency[1]} - Profit in {currency[1]}: '
                  f'{get_arbitrage_info(api_name_1, api_name_2, currency[0], currency[1]):.2f}')
        print("\t------------------------")
        time.sleep(SLEEP_TIME)


def print_ex3(api_name_1, api_name_2):
    print("----EXERCISE 3:")
    common_markets = get_common_markets(get_markets(api_name_1), get_markets(api_name_2))
    ranking = []
    while True:
        for currency in common_markets:
            currency = currency.split("-")
            ranking.append((currency[0], currency[1],
                            get_arbitrage_info(api_name_1, api_name_2, currency[0], currency[1])))
        print(f'\tBuy at {api_name_1}, sell at {api_name_2}')
        ranking.sort(key=lambda elem: elem[2], reverse=True)
        for element in ranking:
            print(f'\t\tBuy {element[0]} for {element[1]} - Profit in {element[1]}: {element[2]:.2f}')
        print("------------------------")
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    print_ex1(APIS.bitbay.name, APIS.bittrex.name)
    try:
        # print_ex2(APIS.bitbay.name, APIS.bittrex.name)  # endless loop - refresh every 5 sec
        print_ex3(APIS.bitbay.name, APIS.bittrex.name)  # endless loop - refresh every 5 sec
    except requests.exceptions:
        print("Connection to APIs failed.")
