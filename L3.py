import requests
import time
from enum import Enum


# Api
API_BITBAY = "https://bitbay.net/API/Public"
REQUEST_ORDERBOOK_BITBAY = "{market}/orderbook.json"
API_BITTREX = "https://api.bittrex.com/v3"
REQUEST_ORDERBOOK_BITTREX = "markets/{market}/orderbook"

# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 4
DIFFERENCE_PRECISION = 2

# Fees
TAKER_FEE_BITBAY = 0.0043
TRANSFER_FEES_BITBAY = {
    "BTC": 0.0005,
    "ETH": 0.01,
    "LTC": 0.001,
    "XRP": 0.1
}

TAKER_FEE_BITTREX = 0.0035
TRANSFER_FEES_BITTREX = {
    "BTC": 0.0005,
    "ETH": 0.006,
    "LTC": 0.01,
    "XRP": 1.0
}


# Other
CRYPTOCURRENCIES = ["BTC", "LTC", "ETH", "XRP"]

# Enums
MARKET_API = Enum("MARKET_API", "BITBAY BITTREX")


def get_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def format_bittrex_orders(orders, quantity=ORDERS_COUNT):
    if orders is not None:
        bids = orders["bid"][:quantity]
        bids_list = list()
        for bid in bids:
            temp_dict = {
                "price": bid["rate"],
                "volume": bid["quantity"]
            }
            bids_list.append(temp_dict)

        asks = orders["ask"][:quantity]
        asks_list = list()
        for ask in asks:
            temp_dict = {
                "price": ask["rate"],
                "volume": ask["quantity"]
            }
            asks_list.append(temp_dict)

        return {"bids": bids_list, "asks": asks_list}
    return None


def format_bitbay_orders(orders, quantity=ORDERS_COUNT):
    if orders is not None:
        bids = orders["bids"][:quantity]
        bids_list = list()
        for bid in bids:
            temp_dict = {
                "price": bid[0],
                "volume": bid[1]
            }
            bids_list.append(temp_dict)

        asks = orders["asks"][:quantity]
        asks_list = list()
        for ask in asks:
            temp_dict = {
                "price": ask[0],
                "volume": ask[1]
            }
            asks_list.append(temp_dict)
        return {"bids": bids_list, "asks": asks_list}
    return None


def get_market_orders(api, cryptocurrency, currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    if api == MARKET_API.BITBAY:
        market = f"{cryptocurrency}{currency}"
        orders = get_data_from_url(f"{API_BITBAY}/{REQUEST_ORDERBOOK_BITBAY.format(market=market)}")
        return format_bitbay_orders(orders, quantity)

    if api == MARKET_API.BITTREX:
        market = f"{cryptocurrency}-{currency}"
        orders = get_data_from_url(f"{API_BITTREX}/{REQUEST_ORDERBOOK_BITTREX.format(market=market)}")
        return format_bittrex_orders(orders, quantity)
    return None


def calculate_difference(new_value, base):
    if base == 0:
        return ZeroDivisionError
    return (1 - (float(new_value) - float(base)) / float(base)) * 100


def ex1a():
    print("BITTREX")
    for crypto in CRYPTOCURRENCIES:
        orders = get_market_orders(MARKET_API.BITTREX, crypto)
        if orders is not None:
            print(f"{crypto}/{BASE_CURRENCY} buy/sell difference")
            best_bid = orders["bids"][0]
            best_ask = orders["asks"][0]
            difference = calculate_difference(best_ask["price"], best_bid["price"])
            print(difference)
        else:
            print(f"{crypto} not found")
    print()


def ex1b():
    print("BITTREX")
    for crypto in CRYPTOCURRENCIES:
        orders = get_market_orders(MARKET_API.BITTREX, crypto)
        if orders is not None:
            print(f"{crypto}/{BASE_CURRENCY} sell/buy difference")
            best_bid = orders["bids"][0]
            best_ask = orders["asks"][0]
            difference = calculate_difference(best_bid["price"], best_ask["price"])
            print(difference)
        else:
            print(f"{crypto} not found")
    print()


def ex1c():
    markets_pair = (MARKET_API.BITBAY, MARKET_API.BITTREX)
    for crypto in CRYPTOCURRENCIES:
        fst_orders = get_market_orders(markets_pair[0], crypto, quantity=1)
        snd_orders = get_market_orders(markets_pair[1], crypto, quantity=1)
        fail_index = -1
        if fst_orders is None:
            fail_index = 0
        if snd_orders is None:
            fail_index = 1
        if fail_index == -1:
#            print("Bitbay: " + str(fst_orders))
#            print("Bitrex: " + str(snd_orders))
            best_bid = fst_orders["bids"][0]
            best_ask = snd_orders["asks"][0]
            diff = (float(best_bid["price"]) - float(best_ask["price"]))\
                / float(best_ask["price"]) * 100
            print(f"{markets_pair[0].name}/{markets_pair[1].name} {crypto}-{BASE_CURRENCY} difference: {diff:.2f}%")

            rev_best_bid = snd_orders["bids"][0]
            rev_best_ask = fst_orders["asks"][0]
            rev_diff = (float(rev_best_bid["price"]) - float(rev_best_ask["price"]))\
                       / float(rev_best_ask["price"]) * 100
            print(f"{markets_pair[1].name}/{markets_pair[0].name} {crypto}-{BASE_CURRENCY} difference: {rev_diff:.2f}%")
#            print(f"Best bid: {best_bid['price']}")
#            print(f"Best ask: {best_ask['price']}")
        else:
            print(f"Failed to get {crypto} data from {markets_pair[fail_index].name}")


def main():
    ex1a()
    ex1b()
    ex1c()


if __name__ == "__main__":
    main()
