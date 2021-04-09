import requests
import time

currency1 = "BTC"
currency2 = "USD"
first_api = "https://bitbay.net/API/Public/{}/orderbook.json".format(currency1 + currency2)
second_api = "https://api.bittrex.com/api/v1.1/public/getticker?market={}-{}".format(currency2, currency1)


def get_offers(api):
    return requests.get(api)


def get_bid_from_bitbay(offer):
    bids = offer.json()['bids']
    return bids[0][0]


def get_ask_from_bitbay(offer):
    asks = offer.json()['asks']
    return asks[0][0]


def get_bid_from_bittrex(offer):
    return (offer.json()['result'])['Bid']


def get_ask_from_bittrex(offer):
    return (offer.json()['result'])['Ask']


def get_difference_in_percent(offer1, offer2):
    return (1 - (offer1 - offer2) / offer2) * 100


def print_spread(offer1, offer2):
    bitbay_bid = get_bid_from_bitbay(offer1)
    bitbay_ask = get_ask_from_bitbay(offer1)
    bittrex_bid = get_bid_from_bittrex(offer2)
    bittrex_ask = get_ask_from_bittrex(offer2)

    print(str(get_difference_in_percent(bitbay_bid, bittrex_bid)) + "%")
    print(str(get_difference_in_percent(bitbay_ask, bittrex_ask)) + "%")
    print(str(get_difference_in_percent(bitbay_bid, bittrex_ask)) + "%")
    print(str(get_difference_in_percent(bittrex_bid, bitbay_ask)) + "%")


if __name__ == '__main__':

    while True:
        offers1 = get_offers(first_api)
        offers2 = get_offers(second_api)
        # print(offers1.json())
        # print(offers2.json())
        print_spread(offers1, offers2)
        print("----------------------------")
        time.sleep(5)
