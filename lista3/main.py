import requests
import time

DELAY = 5
CURRENCY = "BTC"
BASE_CURRENCY = "USD"
FIRST_API = "https://bitbay.net/API/Public/{}/orderbook.json".format(CURRENCY + BASE_CURRENCY)
SECOND_API = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(BASE_CURRENCY, CURRENCY)
BITBAY_FEES = {"taker_fee": 0.0042, "BTC_fee": 0.0005}
BITTREX_FEES = {"taker_fee": 0.0075, "BTC_fee": 0.0005}


def get_offers(api):
    try:
        offers = requests.get(api)
        if 199 < offers.status_code < 300:
            return offers.json()
        else:
            return None
    except requests.exceptions:
        return None


def get_bid_from_bitbay(offer):
    bids = offer['bids']
    return bids[0][0], bids[0][1]


def get_ask_from_bitbay(offer):
    asks = offer['asks']
    return asks[0][0], asks[0][1]


def get_bid_from_bittrex(offer):
    bids = offer['result']['buy']
    return bids[0]['Rate'], bids[0]['Quantity']


def get_ask_from_bittrex(offer):
    asks = offer['result']['sell']
    return asks[0]['Rate'], asks[0]['Quantity']


def get_difference_in_percent(offer1, offer2):
    return (1 - (offer1 - offer2) / offer2) * 100


def possible_arbitrage(selling_price, buying_price):
    return selling_price > buying_price


def bid_with_fees(bid, fees):
    return bid * (1 - fees['taker_fee'] - fees['BTC_fee'])


def ask_with_fees(ask, fees):
    return ask * (1 + fees['taker_fee'] + fees['BTC_fee'])


def get_profit(bid, ask):
    return bid - ask


def get_bids_and_asks(offer1, offer2):
    bitbay_bid = get_bid_from_bitbay(offer1)
    bitbay_ask = get_ask_from_bitbay(offer1)
    bittrex_bid = get_bid_from_bittrex(offer2)
    bittrex_ask = get_ask_from_bittrex(offer2)
    return bitbay_bid, bitbay_ask, bittrex_bid, bittrex_ask


def print_spread(bitbay_bid, bitbay_ask, bittrex_bid, bittrex_ask):
    print("buying difference [%]:")
    print(str(get_difference_in_percent(bitbay_bid[0], bittrex_bid[0])) + "%")

    print("selling difference [%]:")
    print(str(get_difference_in_percent(bitbay_ask[0], bittrex_ask[0])) + "%")

    print("buying at bitbay and selling at bittrex difference [%]:")
    print(str(get_difference_in_percent(bitbay_ask[0], bittrex_bid[0])) + "%")

    print("buying at bittrex and selling at bitbay difference [%]:")
    print(str(get_difference_in_percent(bittrex_ask[0], bitbay_bid[0])) + "%")


def print_arbitrage_info(bitbay_bid, bitbay_ask, bittrex_bid, bittrex_ask):
    print("buying at bitbay and selling at bittrex")
    if possible_arbitrage(bid_with_fees(bittrex_bid[0], BITTREX_FEES), ask_with_fees(bitbay_ask[0], BITBAY_FEES)):
        print("quantity of resources that can be subjected to arbitrage:")
        print(min(bitbay_ask[1], bittrex_bid[1]))
        print("profit [%]:")
        profit = get_profit(bid_with_fees(bittrex_bid[0], BITTREX_FEES), ask_with_fees(bitbay_ask[0], BITBAY_FEES))
        print(profit/ask_with_fees(bitbay_ask[0], BITBAY_FEES))
        print("profit in {}:".format(BASE_CURRENCY))
        print(profit)
    else:
        print("arbitrage not possible")

    print("buying at bittrex and selling at bitbay")
    if possible_arbitrage(bid_with_fees(bitbay_bid[0], BITBAY_FEES), ask_with_fees(bittrex_ask[0], BITTREX_FEES)):
        print("quantity of resources that can be subjected to arbitrage:")
        print(min(bittrex_ask[1], bitbay_bid[1]))
        print("profit [%]:")
        profit = get_profit(bid_with_fees(bitbay_bid[0], BITBAY_FEES), ask_with_fees(bittrex_ask[0], BITTREX_FEES))
        print(profit/ask_with_fees(bittrex_ask[0], BITTREX_FEES))
        print("profit in {}:".format(BASE_CURRENCY))
        print(profit)
    else:
        print("arbitrage not possible")


if __name__ == '__main__':

    while True:
        offers1 = get_offers(FIRST_API)
        offers2 = get_offers(SECOND_API)
        if offers1 and offers2:
            bids_and_asks = get_bids_and_asks(offers1, offers2)
            print_spread(bids_and_asks[0], bids_and_asks[1], bids_and_asks[2], bids_and_asks[3])
            print_arbitrage_info(bids_and_asks[0], bids_and_asks[1], bids_and_asks[2], bids_and_asks[3])
        print("----------------------------")
        time.sleep(DELAY)
