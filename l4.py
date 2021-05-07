import random
import requests
import json

# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 30
DIFFERENCE_PRECISION = 2
INTERVAL = 5
DEFAULT_ORDER_LIMIT = 10
DEFAULT_API_PATH = "api_data.json"
# Decides when two volumes are considered equal
ARBITRAGE_EQUAL_PRECISION = 1.0E-9

# Api
MARKET_API = {}

# Other
CRYPTOCURRENCIES = ["BTC", "LTC", "ETH", "XRP"]


def read_api_data_from_file(filename=DEFAULT_API_PATH):
    global MARKET_API
    try:
        with open(filename) as json_file:
            MARKET_API = json.load(json_file)
    except (FileNotFoundError, IOError, OSError) as e:
        return False
    return True


def get_data_from_url(url):
    response = requests.request("GET", url, headers={'content-type': 'application/json'})
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
        sel_price = "ra"
        sel_volume = "ca"
        sel_bid = "buy"
        sel_ask = "sell"
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


def get_market_orders(api, fst_currency, snd_currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    if api == MARKET_API["BITBAY"]:
        market = f"{fst_currency}-{snd_currency}"
        orders = get_data_from_url(f"{api['url']}{api['orderbook'].format(market=market, limit=DEFAULT_ORDER_LIMIT)}")
        if orders['status'] != "Ok":
            return None
        return format_orders(api, orders, quantity)

    if api == MARKET_API["BITTREX"]:
        market = f"{fst_currency}-{snd_currency}"
        orders = get_data_from_url(f"{api['url']}/{api['orderbook'].format(market=market)}")
        return format_orders(api, orders, quantity)
    return None


# Calculate if arbitrage between two platforms is profitable
def calculate_arbitrage(cryptocurrency, api_bid, api_ask, bids, asks):
    bids_index = 0
    asks_index = 0
    bids_len = len(bids)
    asks_len = len(asks)
    # Total earnings in base currency
    total_profit = 0
    # If it's first calculation, return profit even if it's negative
    first_iteration = True

    # While there are offers
    while bids_index < bids_len and asks_index < asks_len:
        bid = bids[bids_index]
        ask = asks[asks_index]
        # print(f"bid: {bid}", end=", ")
        # print(f"ask: {ask}")
        # Find smallest volume
        volume = float(bid["volume"])
        if float(ask["volume"]) < volume:
            volume = float(ask["volume"])
        # Calculate base profit
        buy_price = volume * float(ask["price"])
        sell_price = volume * float(bid["price"])
        base_profit = sell_price - buy_price

        # Calculate fees
        buy_fee = buy_price * api_ask["taker"] + api_ask["transfer"][cryptocurrency] * float(ask["price"])
        sell_fee = sell_price * api_bid["taker"] + api_bid["transfer"][cryptocurrency] * float(bid["price"])
        total_fee = buy_fee + sell_fee
        # Calculate profit
        current_profit = base_profit - total_fee

        # Stop if profit is not positive
        if current_profit <= 0:
            if first_iteration:
                return current_profit
            return total_profit
        first_iteration = False

        # Move to next offers
        # If volumes were equal
        if abs(float(ask["volume"]) - float(bid["volume"])) <= ARBITRAGE_EQUAL_PRECISION:
            print(f"Equal: {ask['volume']}, {bid['volume']}")
            bids_index += 1
            asks_index += 1
        # If we're left with bid volume
        elif float(ask["volume"]) < float(bid["volume"]):
            bid["volume"] = float(bid["volume"]) - float(ask["volume"])
            asks_index += 1
            print(f"Left bid: {bid}")
        # If we're left with ask volume
        else:
            ask["volume"] = float(ask["volume"]) - float(bid["volume"])
            bids_index += 1
            print(f"Left ask: {ask}")
        total_profit += current_profit
    return total_profit


# Old, remove later
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


# Changes markets format so they look the same no matter which api was used
def format_markets(api, markets):
    if markets is None:
        return None
    markets_list = list()
    if api == MARKET_API["BITBAY"]:
        markets = markets["items"]
        for m in markets:
            markets_list.append(m)
    elif api == MARKET_API["BITTREX"]:
        for m in markets:
            markets_list.append(m["symbol"])
    else:
        return None
    return markets_list


# Returns all markets of given api
def get_all_markets(api):
    if api == MARKET_API["BITBAY"]:
        markets = get_data_from_url(f"{api['url']}{api['markets']}")
        if markets['status'] != "Ok":
            return None
        return format_markets(api, markets)

    if api == MARKET_API["BITTREX"]:
        markets = get_data_from_url(f"{api['url']}{api['markets']}")
        return format_markets(api, markets)
    return None


# Find common value pairs for given market api's
# Returns list of market pairs symbols
def find_common_markets(api_1, api_2):
    common_markets_symbols = []
    markets_api_1 = get_all_markets(api_1)
    markets_api_2 = get_all_markets(api_2)
    for i in markets_api_1:
        for j in markets_api_2:
            # print("Pair: " + str(markets_bitbay['items'][j]['market']['code']) + ", " + str(i['symbol']))
            if j == i:
                # print("Pair: " + str(markets_bitbay['items'][j]['market']['code']) + ", " + str(i['symbol']))
                symbol = i.split("-")
                common_markets_symbols.append((symbol[0], symbol[1]))
                break
    return common_markets_symbols


def lab_4():
    markets_api_list = list(MARKET_API)
    common_markets = list()
    market_pairs_apis = list()
    # Find common markets for each market api pair, store common markets and market api pair
    for api_1_index in range(0, len(MARKET_API) - 1):
        for api_2_index in range(api_1_index + 1, len(MARKET_API)):
            if api_1_index != api_2_index:
                api_1 = MARKET_API[markets_api_list[api_1_index]]
                api_2 = MARKET_API[markets_api_list[api_2_index]]
                common_markets.append(find_common_markets(api_1, api_2))

                # Get 3 random market pairs
                random_pairs = random.sample(range(0, len(common_markets[0])), 3)
                for i in random_pairs:
                    print(common_markets[0][i])
                    # Calculate arbitrage for them
                    crypto, base = common_markets[0][i]
                    fst_orders = get_market_orders(api_1, crypto, base)
                    snd_orders = get_market_orders(api_2, crypto, base)

                    profit = calculate_arbitrage(crypto, api_1, api_2, fst_orders["bids"], snd_orders["asks"])
                    rev_profit = calculate_arbitrage(crypto, api_1, api_2, snd_orders["bids"], fst_orders["asks"])
                    print(f"{profit} {base}")
                    print(f"{rev_profit} {base}")
    # Print all found common market pairs
    #for pair in common_markets:
    #    for symbol in pair:
    #        print(symbol)




# Get current fees for bittrex
def update_bittrex_fees():
    try:
        data = get_data_from_url("https://api.bittrex.com/api/v1.1/public/getcurrencies")["result"]
        for cl in data:
            # print(f"{cl['Currency']} {cl['TxFee']}")
            MARKET_API["BITTREX"]["transfer"][cl["Currency"]] = cl["TxFee"]
        return True
    except KeyError:
        print("Failed to update bittrex fees")
        return False


def save_api_data(file_path=DEFAULT_API_PATH):
    try:
        with open(file_path, "w") as file:
            json.dump(MARKET_API, file, indent=4, sort_keys=True)
    except IOError:
        print("Failed to save updated bittrex fees")


def common_test():
    markets_api_list = list(MARKET_API)
    market_pairs_apis = list()
    common_markets = list()
    # Find common markets for each market api pair, store common markets and market api pair
    for api_1_index in range(0, len(MARKET_API) - 1):
        for api_2_index in range(api_1_index + 1, len(MARKET_API)):
            if api_1_index != api_2_index:
                common_markets = (find_common_markets(markets_api_list[api_1_index], markets_api_list[api_2_index]))
                market_pairs_apis.append((markets_api_list[api_1_index], markets_api_list[api_2_index]))

    print(market_pairs_apis)
    print(common_markets)
    print(len(common_markets))
    return 0
    # For every api in market api, match it with every other api
    for apis in market_pairs_apis:
        fst_api = MARKET_API[apis[0]]
        snd_api = MARKET_API[apis[1]]
        # For every currency in common currencies, calculate arbitrage
        for currencies in common_markets:
            fst_currency = currencies[0]
            snd_currency = currencies[1]
            print(fst_currency)
            print(snd_currency)
            fst_orders = get_market_orders(fst_api, fst_currency, snd_currency, quantity=1)
            snd_orders = get_market_orders(snd_api, fst_currency, snd_currency, quantity=1)
            fail_index = -1
            if fst_orders is None:
                print(fst_api['name'])
                fail_index = 0
            if snd_orders is None:
                print(snd_api['name'])
                fail_index = 1
            if fail_index == -1:
                best_bid = fst_orders["bids"][0]
                best_ask = snd_orders["asks"][0]
                print(f"{fst_api['name']}/{fst_api['name']} {fst_currency}-{snd_currency}")
                profit = calculate_arbitrage(fst_currency, snd_currency, fst_api, snd_api, best_bid, best_ask)

                print()
                rev_best_bid = snd_orders["bids"][0]
                rev_best_ask = fst_orders["asks"][0]
                print(f"{snd_api['name']}/{fst_api['name']} {fst_currency}-{snd_currency}")
                rev_profit = calculate_arbitrage(fst_currency, snd_currency, snd_api, fst_api, rev_best_bid,
                                                 rev_best_ask)
            else:
                print(f"Failed to get {fst_currency} data from {fst_api} {snd_api}")
            print()
        print()


def main():
    read_api_data_from_file()
    fees_updated = update_bittrex_fees()
    if fees_updated:
        save_api_data()

    lab_4()
    #common_test()
    #ex2()



if __name__ == "__main__":
    main()
