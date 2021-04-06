import requests
from enum import Enum


# Api
API_BITBAY = "https://bitbay.net/API/Public"
REQUEST_ORDERBOOK_BITBAY = "{market}/orderbook.json"
API_BITTREX = "https://api.bittrex.com/v3"
REQUEST_ORDERBOOK_BITTREX = "markets/{market}/orderbook"

# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 4

# Other
CRYPTOCURRENCIES = ["BTC", "LTC", "DASH", "XRP", "BCC"]

# Enums
MARKET_API = Enum("MARKET_API", "BITBAY BITTREX")


def get_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_bittrex_orders(cryptocurrency, currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    market = f"{cryptocurrency}-{currency}"
    orders = get_data_from_url(f"{API_BITTREX}/{REQUEST_ORDERBOOK_BITTREX.format(market=market)}")
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


def get_bitbay_orders(cryptocurrency, currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    market = f"{cryptocurrency}{currency}"
    orders = get_data_from_url(f"{API_BITBAY}/{REQUEST_ORDERBOOK_BITBAY.format(market=market)}")
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
        return get_bittrex_orders(cryptocurrency, currency, quantity)

    if api == MARKET_API.BITTREX:
        return get_bittrex_orders(cryptocurrency, currency, quantity)
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


def main():
    ex1a()
    ex1b()


if __name__ == "__main__":
    main()
