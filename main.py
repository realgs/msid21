import requests
import time


API_1 = {
    'name': "BITBAY",
    'url': "https://bitbay.net/API/Public/{}{}/orderbook.json",
    'taker_fee': 0.0043,
    'transfer_fee': 0.0005
}
API_2 = {
    'name': "BITTREX",
    'url': "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both",
    'taker_fee': 0.0025,
    'transfer_fee': 0.0005
}
BASE_CURRENCY = "USD"
CRYPTO_CURRENCY = "BTC"
SINGLE_OFFER = 1
SLEEP_TIME = 5


def get_response(url):
    api_response = requests.get(url)
    if 200 <= api_response.status_code <= 299:
        return api_response.json()
    else:
        print("Could not connect to API.", api_response.reason)
        return None


def get_offers(api_name, no_of_offers):
    if api_name == API_1['name']:
        all_offers = get_response(API_1['url'].format(CRYPTO_CURRENCY, BASE_CURRENCY))
        if all_offers is not None:
            return {'bids': (all_offers['bids'][:no_of_offers]), 'asks': (all_offers['asks'][:no_of_offers])}
    else:
        all_offers = get_response(API_2['url'].format(BASE_CURRENCY, CRYPTO_CURRENCY))
        if all_offers is not None:
            tmp = {'bids': [], 'asks': []}
            for i in range(no_of_offers):
                bids_list = list(all_offers['result']['buy'][i].values())
                bids_list.reverse()
                asks_list = list(all_offers['result']['sell'][i].values())
                asks_list.reverse()
                tmp['bids'].append(bids_list)
                tmp['asks'].append(asks_list)
            return tmp


def get_buy_sell_ratio(api_name_1, api_name_2, offer_type):
    offer_api_1 = get_offers(api_name_1, SINGLE_OFFER)
    offer_api_2 = get_offers(api_name_2, SINGLE_OFFER)
    if offer_api_1 is None or offer_api_2 is None:
        return None
    else:
        return (offer_api_1[offer_type][0][1] - offer_api_2[offer_type][0][1]) / offer_api_1[offer_type][0][1] * 100


def get_arbitrage_ratio(api_name_1, api_name_2):
    offer_api_1 = get_offers(api_name_1, SINGLE_OFFER)
    offer_api_2 = get_offers(api_name_2, SINGLE_OFFER)
    if offer_api_1 is None or offer_api_2 is None:
        return None
    else:
        return (offer_api_2['bids'][0][1] - offer_api_1['asks'][0][1]) / offer_api_2['bids'][0][1] * 100


def include_fees(api_name, fee_name, cost):
    if fee_name == "taker_fee":
        if api_name == API_1['name']:
            return cost * (1 + API_1['taker_fee'])
        else:
            return cost * (1 + API_2['taker_fee'])
    else:
        if api_name == API_1['name']:
            return cost - API_1['transfer_fee']
        else:
            return cost - API_2['transfer_fee']


def get_arbitrage_info(api_name_1, api_name_2):
    offer_api_1 = get_offers(api_name_1, SINGLE_OFFER)
    offer_api_2 = get_offers(api_name_2, SINGLE_OFFER)
    amount = min(offer_api_1['asks'][0][1], offer_api_2['bids'][0][1])
    spent = include_fees(api_name_1, "taker", offer_api_1['asks'][0][1]) * amount
    earned = include_fees(api_name_2, "transfer", offer_api_2['bids'][0][1]) * amount
    return {'amount': amount, 'USD': earned - spent, 'profit': (earned - spent) / spent * 100}


def print_ex1(api_name_1, api_name_2):
    print("----EXERCISE 1:")
    print("\ta)", f'{api_name_1} to {api_name_2} buy ratio for {CRYPTO_CURRENCY}{BASE_CURRENCY}: '
                  f'{get_buy_sell_ratio(api_name_1, api_name_2, "bids"):.2f}%')
    print("\tb)", f'{api_name_1} to {api_name_2} sell ratio for {CRYPTO_CURRENCY}{BASE_CURRENCY}: '
                  f'{get_buy_sell_ratio(api_name_1, api_name_2, "asks"):.2f}%')
    print("\tc)", f'{api_name_1} to {api_name_2} arbitrage ratios for {CRYPTO_CURRENCY}{BASE_CURRENCY}:')
    print(f'\tBuy at {api_name_1}, sell at {api_name_2}: {get_arbitrage_ratio(api_name_1, api_name_2):.2f}%')
    print(f'\tBuy at {api_name_2}, sell at {api_name_1}: {get_arbitrage_ratio(api_name_2, api_name_1):.2f}%')


def print_ex2(api_name_1, api_name_2):
    print("----EXERCISE 2:")
    buy_at_1_sell_at_2 = get_arbitrage_info(api_name_1, api_name_2)
    sell_at_1_buy_at_2 = get_arbitrage_info(api_name_2, api_name_1)
    print(f'\tBuy at {api_name_1}, sell at {api_name_2}:\n\tResource quantity: {buy_at_1_sell_at_2["amount"]}, '
          f'profit: {buy_at_1_sell_at_2["profit"]:.2f}%, profit in USD: {buy_at_1_sell_at_2["USD"]:.10f}$')
    print(f'\tBuy at {api_name_2}, sell at {api_name_1}:\n\tResource quantity: {sell_at_1_buy_at_2["amount"]}, '
          f'profit: {sell_at_1_buy_at_2["profit"]:.2f}%, profit in USD: {sell_at_1_buy_at_2["USD"]:.10f}$')


def print_ex1_ex2(api_name_1, api_name_2):
    while True:
        print_ex1(api_name_1, api_name_2)
        print_ex2(api_name_1, api_name_2)
        print("------------------------")
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    try:
        print_ex1_ex2(API_1['name'], API_2['name'])  # endless loop - refresh every 5 sec
    except requests.exceptions:
        print("Connection to APIs failed.")
