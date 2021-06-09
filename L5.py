from json import JSONDecodeError
import json
import requests
import time
import yfinance as yf

# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 30
DEFAULT_API_PATH = "api_data.json"

# Wallet path
DEFAULT_CONFIG_PATH = "config.json"

# Decides when two volumes are considered equal
VOLUMES_EQUAL_PRECISION = 1.0E-9
# Api
MARKET_API = {}

# Available resource types
RES_TYPES = {"crypto": "crypto", "currency": "currency", "us": "us"}


def get_data_from_url(url):
    response = requests.request("GET", url, headers={'content-type': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Format given orders depending on api
def format_orders(api, orders, quantity=ORDERS_COUNT):
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


# Get specific amount of market orders from given api, in universal format
def get_market_orders(api, fst_currency, snd_currency=BASE_CURRENCY, quantity=ORDERS_COUNT):
    if api == MARKET_API["BITBAY"]:
        market = f"{fst_currency}-{snd_currency}"
        orders = get_data_from_url(f"{api['url']}{api['orderbook'].format(market=market)}")
        if orders is None:
            return orders
        if orders['status'] != "Ok":
            return None
        return format_orders(api, orders, quantity)

    if api == MARKET_API["BITTREX"]:
        market = f"{fst_currency}-{snd_currency}"
        orders = get_data_from_url(f"{api['url']}/{api['orderbook'].format(market=market)}")
        return format_orders(api, orders, quantity)
    return None


# Calculate if arbitrage between two platforms is profitable
# Return profit in percentage
def calculate_arbitrage(cryptocurrency, api_bid, api_ask, bids, asks):
    bids_index = 0
    asks_index = 0
    bids_len = len(bids)
    asks_len = len(asks)
    # Total earnings in base currency
    total_profit = 0
    # Total cost of buying
    total_buy_price = 0
    # Total cost of fees
    total_fee = 0
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
        total_buy_price += buy_price
        sell_price = volume * float(bid["price"])
        base_profit = sell_price - buy_price

        # Calculate fees
        buy_fee = buy_price * api_ask["taker"] + api_ask["transfer"][cryptocurrency] * float(ask["price"])
        sell_fee = sell_price * api_bid["taker"] + api_bid["transfer"][cryptocurrency] * float(bid["price"])
        current_fee = buy_fee + sell_fee
        total_fee += current_fee
        # Calculate profit
        current_profit = base_profit - current_fee

        # Stop if profit is not positive
        if current_profit <= 0:
            if first_iteration:
                return current_profit / (buy_price + current_fee) * 100
            return total_profit
        first_iteration = False

        # Move to the next offers
        # If volumes were equal
        if abs(float(ask["volume"]) - float(bid["volume"])) <= VOLUMES_EQUAL_PRECISION:
            # print(f"Equal: {ask['volume']}, {bid['volume']}")
            bids_index += 1
            asks_index += 1
        # If we're left with bid volume
        elif float(ask["volume"]) < float(bid["volume"]):
            bid["volume"] = float(bid["volume"]) - float(ask["volume"])
            asks_index += 1
            # print(f"Left bid: {bid}")
        # If we're left with ask volume
        else:
            ask["volume"] = float(ask["volume"]) - float(bid["volume"])
            bids_index += 1
            # print(f"Left ask: {ask}")
        total_profit += current_profit
    return total_profit / (total_buy_price + total_fee) * 100


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


# Print arbitrages ranking in user friendly format
def print_ranking(arbitrages_list):
    for i in range(0, len(arbitrages_list)):
        a = arbitrages_list[i]
        print("{0:.2f}% {1}-{2} {3} {4} ".format(a['profit'], a['currency'], a['base'], a['fst_api'], a['snd_api']))


# Calculates arbitrage for all common markets, finds best profit and saves to arbitrages_list
def calculate_arbitrage_for_apis(api_1, api_2, common_markets, common_markets_index, arbitrages_list):
    limit = api_1["limit"]
    if api_2["limit"] < api_1["limit"]:
        limit = api_2["limit"]

    for i in range(0, len(common_markets[common_markets_index])):
        # print(common_markets[common_markets_index][i])
        crypto, base = common_markets[common_markets_index][i]

        # Get market orders
        fst_orders = get_market_orders(api_1, crypto, base)
        snd_orders = get_market_orders(api_2, crypto, base)

        if fst_orders is None:
            print(f"Failed to get {crypto} {base} data from {api_1['name']}")
        elif snd_orders is None:
            print(f"Failed to get {crypto} {base} data from {api_2['name']}")
        else:
            # Calculate possible profit from arbitrage
            profit = calculate_arbitrage(crypto, api_1, api_2, fst_orders["bids"], snd_orders["asks"])
            rev_profit = calculate_arbitrage(crypto, api_1, api_2, snd_orders["bids"], fst_orders["asks"])
            # Check which way it's more beneficial to do arbitrage
            if rev_profit > profit:
                profit = rev_profit
                temp = api_1
                api_1 = api_2
                api_2 = temp
            # Save profit to list with information about apis and currencies
            arbitrages_list.append({
                "fst_api": api_1["name"],
                "snd_api": api_2["name"],
                "currency": crypto,
                "base": base,
                "profit": profit
            })
            # print(f"{profit} {base}")
            # print(f"{rev_profit} {base}")
        # Sleep for 1 second in order to not get banned for too many requests
        if i % limit == 0:
            time.sleep(1)


def lab_4():
    markets_api_list = list(MARKET_API)
    common_markets = list()
    arbitrages_list = list()
    # Find common markets for each market api pair, store common markets
    common_markets_index = 0
    for api_1_index in range(0, len(MARKET_API) - 1):
        for api_2_index in range(api_1_index + 1, len(MARKET_API)):
            if api_1_index != api_2_index:
                api_1 = MARKET_API[markets_api_list[api_1_index]]
                api_2 = MARKET_API[markets_api_list[api_2_index]]
                common_markets.append(find_common_markets(api_1, api_2))

                # print(f"{api_1['name']} {api_2['name']}")

                # Get all market pairs and calculate arbitrage for them
                calculate_arbitrage_for_apis(api_1, api_2, common_markets, common_markets_index, arbitrages_list)
            common_markets_index += 1

    arbitrages_list.sort(key=lambda x: x['profit'], reverse=True)
    print_ranking(arbitrages_list)


# Get current fees for bittrex
def update_bittrex_fees():
    try:
        url = "{0}{1}".format(MARKET_API["BITTREX"]["url"], MARKET_API["BITTREX"]["fees_url"])
        data = get_data_from_url(url)
        if data is None:
            return False
        for cl in data:
            MARKET_API["BITTREX"]["transfer"][cl["symbol"]] = float(cl["txFee"])
        return True
    except KeyError:
        return False


# Read api configuration file
def read_api_data_from_file(filename=DEFAULT_API_PATH):
    global MARKET_API
    try:
        with open(filename) as json_file:
            MARKET_API = json.load(json_file)
    except (FileNotFoundError, IOError, OSError):
        return False
    return True


# Save current api data
def save_api_data(file_path=DEFAULT_API_PATH):
    try:
        with open(file_path, "w") as file:
            json.dump(MARKET_API, file, indent=4, sort_keys=True)
            return True
    except (FileNotFoundError, IOError, OSError):
        return False


# Read user resources, if successful return dictionary
def read_wallet(file_path=DEFAULT_CONFIG_PATH):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)["wallet"]
            return data
    except (FileNotFoundError, IOError, OSError, JSONDecodeError):
        return None


# Save user resources, return true if successful
def save_wallet(wallet, file_path=DEFAULT_CONFIG_PATH):
    try:
        with open(file_path, "w") as file:
            data = {"wallet": wallet}
            json.dump(data, file, indent=4, sort_keys=True)
            return True
    except (IOError, OSError):
        return False


# Sell given currency using best exchange for given api
def sell_currency(api, currency):
    c_buy = currency["volume"] * currency["price"]
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0
    }
    if api == MARKET_API["NBP"]:
        nbp = MARKET_API["NBP"]
        data = get_data_from_url("{0}{1}/C/{2}".format(nbp["url"], nbp["currency"], currency["symbol"]))
        # Unable to read data
        if data is None:
            return no_sell_data
        data = data["rates"][0]

        # If base is not pln exchange to pln
        if currency["base"] != "PLN":
            exchange_data = get_data_from_url("{0}{1}/C/{2}".format(nbp["url"], nbp["currency"], currency["base"]))
            if exchange_data is None:
                return no_sell_data
            exchange_data = exchange_data["rates"][0]
            exchange_ask = exchange_data["ask"]

            old_price = currency["price"]
            price = data["bid"] / exchange_ask
            value = price * currency["volume"]
            buy_cost = currency["volume"] * old_price
            profit = value - buy_cost
        else:
            price = data["bid"]
            value = price * currency["volume"]
            buy_cost = currency["volume"] * currency["price"]
            profit = value - buy_cost

        sell_data = {
            "price": price,
            "value": value,
            "buy_cost": buy_cost,
            "profit": profit
        }
        return sell_data
    # Api not supported
    else:
        return no_sell_data


# Sell given cryptocurrency using best exchange for given api
def sell_crypto(api, crypto, amount=1.0):
    c_buy = crypto["volume"] * crypto["price"] * amount
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0
    }
    offers = get_market_orders(api, crypto["symbol"], crypto["base"])
    if offers is None:
        return no_sell_data
    offers = offers["bids"]
    has_volume = True

    i = 0
    off_len = len(offers)
    volume_left = crypto["volume"] * amount
    value = 0.0
    while has_volume and i < off_len:
        offer = offers[i]
        offer_volume = float(offer["volume"])
        offer_price = float(offer["price"])
        # If no volume left
        if volume_left - offer_volume < 0:
            value += offer_price * volume_left
            volume_left = 0.0
            has_volume = False
        # Normal case
        else:
            volume_left -= offer_volume
            value += offer_price * offer_volume
        i += 1
    # If run out of offers
    if has_volume:
        value += offer_price * volume_left
    price = offer_price
    profit = value - c_buy
    sell_data = {
        "price": price,
        "value": value,
        "buy_cost": c_buy,
        "profit": profit
    }
    return sell_data


# Find possible resource sale in apis
def find_offers_for_wallet(wallet, amount):
    sell_data = {}
    for res in wallet:
        resource = wallet[res]
        for api in MARKET_API:
            types = MARKET_API[api]["type"]
            # If resource is in api
            if resource["type"] in types:
                # If resource is cryptocurrency
                if resource["type"] == RES_TYPES["crypto"]:
                    pass
                    data = sell_crypto(MARKET_API[api], resource, amount)
                    sell_data[res] = data
                # If resource is currency
                elif resource["type"] == RES_TYPES["currency"]:
                    data = sell_currency(MARKET_API[api], resource)
                    sell_data[res] = data
    print_wallet_sell_options(wallet, sell_data)


# Add new resource to the wallet
def add_resource(wallet):
    res_symbol = input("Enter resource symbol: ")
    res_symbol = res_symbol.strip()
    if res_symbol in wallet:
        print("Resource is already in wallet")
        return False

    print("Types: {0}".format(list(RES_TYPES.values())))
    res_type = input("Enter resource type: ")
    res_type = res_type.strip()
    if res_type not in RES_TYPES:
        print("Invalid type")
        return False

    res_volume = input("Enter resource volume: ")
    res_volume = res_volume.strip()
    try:
        res_volume = float(res_volume)
    except ValueError:
        print("Invalid volume")
        return False

    res_price = input("Enter resource price: ")
    res_price = res_price.strip()
    try:
        res_price = float(res_price)
    except ValueError:
        print("Invalid price")
        return False

    res_base = input("Enter resource base currency: ")
    res_base = res_base.strip()

    res = {
        "type": res_type,
        "symbol": res_symbol,
        "volume": res_volume,
        "price": res_price,
        "base": res_base
    }

    wallet[res_symbol] = res
    return True


def print_wallet_sell_options(wallet, sell_data):
    table = "Wallet sell options\n"
    table += "-" * 80
    table += "\n|{:>8}| {:>8}| {:>15}| {:>10}| {:>8}| {:>12}| {:>12}| {:>10}|\n".format("type", "symbol", "volume", "price", "base", "sell price", "sell value", "profit")
    for key in wallet:
        res = wallet[key]
        s_data = sell_data[key]
        table += ("|{:>8}| {:>8}| {:>15.8f}| {:>10.4f}| {:>8}| {:>12.4f}| {:>12.2f}| {:>10.2f}|\n"
                  .format(res["type"], res["symbol"], res["volume"], res["price"], res["base"], s_data["price"], s_data["value"], s_data["profit"]))
    table += "-" * 80
    print(table)
    return table


# Return wallet data in table format
def print_wallet(wallet):
    table = "Wallet\n"
    table += "-" * 65
    table += "\n|{:>4}| {:>8}| {:>8}| {:>15}| {:>10}| {:>8}|\n".format("nr", "type", "symbol", "volume", "price", "base")
    i = 1
    for key in wallet:
        res = wallet[key]
        table += ("|{:>4}| {:>8}| {:>8}| {:>15.8f}| {:>10.2f}| {:>8}|\n".format(i, res["type"], res["symbol"], res["volume"], res["price"], res["base"]))
        i += 1
    table += "-" * 65
    print(table)
    return table


def menu(wallet):
    while True:
        print()
        print("1. Wallet")
        print("2. Find offers")
        print("3. Add resource")
        print("4. Exit")
        option = input("Please choose option: ")
        try:
            option = int(option.strip())
        except ValueError:
            print("Invalid option")
        if option == 1:
            print_wallet(wallet)
        elif option == 2:
            amount = input("Insert amount to sell (0 - 1.0): ")
            try:
                amount = float(amount.strip())
                if amount < 0 or amount > 1.0:
                    raise ValueError
                find_offers_for_wallet(wallet, amount)
            except ValueError:
                print("Incorrect amount")

        elif option == 3:
            add_resource(wallet)
            if not save_wallet(wallet):
                print("Error while saving new resource")
        elif option == 4:
            exit(0)


def main():
    if not read_api_data_from_file():
        print("Critical error, failed to read {0}".format(DEFAULT_API_PATH))
        return
    if update_bittrex_fees():
        if not save_api_data():
            print("Failed to save updated bittrex fees")
    else:
        print("Failed to update bittrex fees")
    #lab_4()
    wallet = read_wallet()
    if wallet is None:
        print("Unable to read config file {0}".format(DEFAULT_CONFIG_PATH))
        return
    menu(wallet)


if __name__ == "__main__":
    main()
