import requests
import time
from threading import Thread

# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 4
DIFFERENCE_PRECISION = 2
INTERVAL = 5

# Api
MARKET_API = {
    "BITBAY": {
        "name": "BITBAY",
        "url": "https://bitbay.net/API/Public",
        "orderbook": "{market}/orderbook.json",
        "taker": 0.0043,
        "transfer": {
            "BTC": 0.0005,
            "ETH": 0.01,
            "LTC": 0.001,
            "XRP": 0.1
        }
    },
    "BITTREX": {
        "name": "BITTREX",
        "url": "https://api.bittrex.com/v3",
        "orderbook": "markets/{market}/orderbook",
        "taker": 0.0035,
        "transfer": {
            "BTC": 0.0005,
            "ETH": 0.006,
            "LTC": 0.01,
            "XRP": 1.0
        }
    }
}

# Other
CRYPTOCURRENCIES = ["BTC", "LTC", "ETH", "XRP"]


def get_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def format_orders(api, orders, quantity=ORDERS_COUNT):
    sel_price = ""
    sel_volume = ""
    sel_bid = "bid"
    sel_ask = "ask"
    if api == MARKET_API["BITBAY"]:
        sel_price = 0
        sel_volume = 1
        sel_bid = "bids"
        sel_ask = "asks"
    elif api == MARKET_API["BITTREX"]:
        sel_price = "rate"
        sel_volume = "quantity"
        sel_bid = "bid"
        sel_ask = "ask"
    else:
        return None
    if orders is not None:
        bids = orders[sel_bid][:quantity]
        bids_list = list()
        for bid in bids:
            temp_dict = {
                "price": bid[sel_price],
                "volume": bid[sel_volume]
            }
            bids_list.append(temp_dict)

        asks = orders[sel_ask][:quantity]
        asks_list = list()
        for ask in asks:
            temp_dict = {
                "price": ask[sel_price],
                "volume": ask[sel_volume]
            }
            asks_list.append(temp_dict)
        return {"bids": bids_list, "asks": asks_list}
    return None


def get_market_orders(api, cryptocurrency, currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    if api == MARKET_API["BITBAY"]:
        market = f"{cryptocurrency}{currency}"
        orders = get_data_from_url(f"{api['url']}/{api['orderbook'].format(market=market)}")
        return format_orders(api, orders, quantity)

    if api == MARKET_API["BITTREX"]:
        market = f"{cryptocurrency}-{currency}"
        orders = get_data_from_url(f"{api['url']}/{api['orderbook'].format(market=market)}")
        return format_orders(api, orders, quantity)
    return None


def calculate_difference(new_value, base):
    if base == 0:
        return ZeroDivisionError
    return (1 - (float(new_value) - float(base)) / float(base)) * 100


def calculate_arbitrage(cryptocurrency, base_currency, api_bid, api_ask, bid, ask):
    volume = float(bid["volume"])
    if float(ask["volume"]) < volume:
        volume = float(ask["volume"])
    buy_price = volume * float(ask["price"])
    sell_price = volume * float(bid["price"])
    base_profit = sell_price - buy_price

    buy_fee = buy_price * api_ask["taker"] + api_ask["transfer"][cryptocurrency] * float(ask["price"])
    sell_fee = sell_price * api_bid["taker"] + api_bid["transfer"][cryptocurrency] * float(bid["price"])
    total_fee = buy_fee + sell_fee
    total_profit = base_profit - total_fee

    print(f"Arbitrage maximal volume: {volume}")
    print(f"Profit: {(total_profit / (buy_price + total_fee) * 100):.2f}%")
    print(f"Profit: {total_profit:.2f} {base_currency} (in base currency)")
    return total_profit


def repeat_function(function, interval=INTERVAL):
    while True:
        function()
        time.sleep(interval)


def ex1a():
    print("BITTREX")
    for crypto in CRYPTOCURRENCIES:
        orders = get_market_orders(MARKET_API["BITTREX"], crypto)
        if orders is not None:
            print(f"{crypto}/{BASE_CURRENCY} buy/sell difference")
            best_bid = orders["bids"][0]
            best_ask = orders["asks"][0]
            difference = calculate_difference(best_ask["price"], best_bid["price"])
            print(f"{difference:.2f}%")
        else:
            print(f"{crypto} not found")
    print()


def ex1b():
    print("BITTREX")
    for crypto in CRYPTOCURRENCIES:
        orders = get_market_orders(MARKET_API["BITTREX"], crypto)
        if orders is not None:
            print(f"{crypto}/{BASE_CURRENCY} sell/buy difference")
            best_bid = orders["bids"][0]
            best_ask = orders["asks"][0]
            difference = calculate_difference(best_bid["price"], best_ask["price"])
            print(f"{difference:.2f}%")
        else:
            print(f"{crypto} not found")
    print()


def ex1c():
    markets_pair = (MARKET_API["BITBAY"], MARKET_API["BITTREX"])
    for crypto in CRYPTOCURRENCIES:
        fst_orders = get_market_orders(markets_pair[0], crypto, quantity=1)
        snd_orders = get_market_orders(markets_pair[1], crypto, quantity=1)
        fail_index = -1
        if fst_orders is None:
            fail_index = 0
        if snd_orders is None:
            fail_index = 1
        if fail_index == -1:
            best_bid = fst_orders["bids"][0]
            best_ask = snd_orders["asks"][0]
            diff = (float(best_bid["price"]) - float(best_ask["price"])) \
                / float(best_ask["price"]) * 100
            print(f"{markets_pair[0]['name']}/{markets_pair[1]['name']} {crypto}-{BASE_CURRENCY} difference: {diff:.2f}%")

            rev_best_bid = snd_orders["bids"][0]
            rev_best_ask = fst_orders["asks"][0]
            rev_diff = (float(rev_best_bid["price"]) - float(rev_best_ask["price"])) \
                / float(rev_best_ask["price"]) * 100
            print(f"{markets_pair[1]['name']}/{markets_pair[0]['name']} {crypto}-{BASE_CURRENCY} difference: {rev_diff:.2f}%")
        else:
            print(f"Failed to get {crypto} data from {markets_pair[fail_index]['name']}")
    print()


def ex2():
    markets_pair = (MARKET_API["BITBAY"], MARKET_API["BITTREX"])
    for crypto in CRYPTOCURRENCIES:
        fst_orders = get_market_orders(markets_pair[0], crypto, quantity=1)
        snd_orders = get_market_orders(markets_pair[1], crypto, quantity=1)
        fail_index = -1
        if fst_orders is None:
            fail_index = 0
        if snd_orders is None:
            fail_index = 1
        if fail_index == -1:
            best_bid = fst_orders["bids"][0]
            best_ask = snd_orders["asks"][0]
            print(f"{markets_pair[0]['name']}/{markets_pair[1]['name']} {crypto}-{BASE_CURRENCY}")
            profit = calculate_arbitrage(crypto, BASE_CURRENCY, markets_pair[0], markets_pair[1], best_bid, best_ask)

            print()
            rev_best_bid = snd_orders["bids"][0]
            rev_best_ask = fst_orders["asks"][0]
            print(f"{markets_pair[1]['name']}/{markets_pair[0]['name']} {crypto}-{BASE_CURRENCY}")
            rev_profit = calculate_arbitrage(crypto, BASE_CURRENCY, markets_pair[1], markets_pair[0], rev_best_bid, rev_best_ask)
        else:
            print(f"Failed to get {crypto} data from {markets_pair[fail_index]['name']}")
        print()
    print()


def lab_3():
    ex1a()
    ex1b()
    ex1c()
    ex2()


def main():
    thread_bg = Thread(target=repeat_function, args=[lab_3], daemon=True)
    thread_bg.start()
    time.sleep(7)
    input("\nType exit and press enter to exit program\n")


if __name__ == "__main__":
    main()
