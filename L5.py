from json import JSONDecodeError
import json
import requests
import time
import yfinance as yf
from bs4 import BeautifulSoup


# Default variables
BASE_CURRENCY = "USD"
ORDERS_COUNT = 30
DEFAULT_API_PATH = "api_data.json"
TAX = 0.19

# Wallet path
DEFAULT_CONFIG_PATH = "config.json"

# Decides when two volumes are considered equal
VOLUMES_EQUAL_PRECISION = 1.0E-9
# Api
MARKET_API = {}

# Available resource types
RES_TYPES = {"crypto": "crypto", "currency": "currency", "us": "us", "pl": "pl"}


def get_data_from_url(url):
    response = requests.request("GET", url, headers={'content-type': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_text_from_url(url):
    response = requests.request("GET", url)
    if response.status_code == 200:
        return response.text
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
def sell_currency(api, currency, amount=1.0):
    c_buy = currency["volume"] * currency["price"] * amount
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0,
        "api": api["name"][:4],
        "net": 0
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
            value = price * currency["volume"] * amount
            buy_cost = currency["volume"] * old_price * amount
            profit = value - buy_cost
        else:
            price = data["bid"]
            value = price * currency["volume"] * amount
            buy_cost = currency["volume"] * currency["price"] * amount
            profit = value - buy_cost

        net = profit * (1 - TAX)
        sell_data = {
            "price": price,
            "value": value,
            "buy_cost": buy_cost,
            "profit": profit,
            "api": api["name"][:4],
            "net": net
        }
        return sell_data
    # Api not supported
    else:
        return no_sell_data


# Sell given cryptocurrency using best exchange for given api
def sell_crypto(api, crypto, amount=1.0):
    c_buy = crypto["volume"] * crypto["price"] * amount
    net = c_buy * (1 - TAX)
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0,
        "api": api["name"][:4],
        "net": 0
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
    net = profit * (1 - TAX)
    sell_data = {
        "price": price,
        "value": value,
        "buy_cost": c_buy,
        "profit": profit,
        "api": api["name"][:4],
        "net": net
    }
    return sell_data


# Sell given stock using average exchange for given api
def sell_us_stock(api, stock, amount):
    c_buy = stock["volume"] * stock["price"] * amount
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0,
        "api": api["name"][:4],
        "net": 0
    }
    if api == MARKET_API["YAHOO"]:
        try:
            res = yf.Ticker(stock["symbol"])
        except KeyError:
            return no_sell_data
        average_price = (res.info["previousClose"] + res.info["open"]) / 2
        value = average_price * stock["volume"] * amount
        profit = value - c_buy
        net = profit * (1 - TAX)
        sell_data = {
            "price": average_price,
            "value": value,
            "buy_cost": c_buy,
            "profit": profit,
            "api": api["name"][:4],
            "net": net
        }
        return sell_data
    return no_sell_data


# Sell given stock using average exchange for given api
def sell_pl_stock(api, stock, amount):
    c_buy = stock["volume"] * stock["price"] * amount
    no_sell_data = {
        "price": 0,
        "value": 0,
        "buy_cost": c_buy,
        "profit": 0,
        "api": api["name"][:4],
        "net": 0
    }
    if api == MARKET_API["STOOQ"]:
        try:
            data = get_text_from_url("{0}/q/?s={1}".format(api["url"], stock["symbol"]))
            data = BeautifulSoup(data, "html.parser")
            data = float(data.find(id="t1").find('td').find('span').text)
        except Exception:
            return no_sell_data
        price = data
        value = price * stock["volume"] * amount
        profit = value - c_buy
        net = profit * (1 - TAX)
        sell_data = {
            "price": price,
            "value": value,
            "buy_cost": c_buy,
            "profit": profit,
            "api": api["name"][:4],
            "net": net
        }
        return sell_data
    return no_sell_data


# Find best possible resource sale in apis
def find_offers_for_wallet(wallet, amount):
    sell_data = {}
    for res in wallet:
        resource = wallet[res]
        for api in MARKET_API:
            types = MARKET_API[api]["type"]
            # If resource is in api
            data = None
            if resource["type"] in types:
                # If resource is cryptocurrency
                if resource["type"] == RES_TYPES["crypto"]:
                    data = sell_crypto(MARKET_API[api], resource, amount)
                # If resource is currency
                elif resource["type"] == RES_TYPES["currency"]:
                    data = sell_currency(MARKET_API[api], resource, amount)
                # If resource is us market stock
                elif resource["type"] == RES_TYPES["us"]:
                    data = sell_us_stock(MARKET_API[api], resource, amount)
                # If resource is us market stock
                elif resource["type"] == RES_TYPES["pl"]:
                    data = sell_pl_stock(MARKET_API[api], resource, amount)

            best = sell_data.get(res, None)
            if best is not None and data is not None:
                # Choose better offer
                if best["profit"] < data["profit"]:
                    sell_data[res] = data
            elif data is not None:
                sell_data[res] = data
        # Resource not in any api
        if sell_data.get(res, None) is None:
            sell_data[res] = None
    print_wallet_sell_options(wallet, sell_data, amount)


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


# Print wallet resources and sell options in table
def print_wallet_sell_options(wallet, sell_data, amount=1.0):
    value_sum = 0.0
    profit_sum = 0.0

    table = "\nWallet sell options\n"
    table += "Sell amount: {:.3f}%\n".format(amount*100)
    table += "-" * 118
    table += "\n|{:>8}| {:>8}| {:>15}| {:>12}| {:>6}| {:>12}| {:>12}| {:>10}| {:>10}| {:>5}|\n"\
        .format("Symbol", "Type", "Volume", "Price", "Base", "Sell price", "Sell value", "Profit", "Net profit", "Api")
    for key in wallet:
        s_data = sell_data[key]
        res = wallet[key]
        if s_data is not None:
            value_sum += s_data["value"]
            profit_sum += s_data["profit"]
            table += ("|{:>8}| {:>8}| {:>15.6f}| {:>12.4f}| {:>6}| {:>12.4f}| {:>12.2f}| {:>10.2f}| {:>10.2f}| {:>5}|\n"
                      .format(res["symbol"], res["type"], res["volume"], res["price"], res["base"], s_data["price"], s_data["value"], s_data["profit"], s_data["net"], s_data["api"]))
        # No data for resource
        else:
            table += ("|{:>8}| {:>8}| {:>15.6f}| {:>12.4f}| {:>6}| {:>12.2f}| {:>12.2f}| {:>10.2f}| {:>10.2f}| {:>5}|\n"
                      .format(res["symbol"], res["type"], res["volume"], res["price"], res["base"], 0.0, 0.0, 0.0, 0.0, s_data["api"]))
    table += "-" * 118
    # table += "\nTotal value: {:.2f}\n".format(value_sum)
    # table += "Total profit: {:.2f}\n".format(profit_sum)
    table += "\n"
    print(table)
    return table


# Return wallet data in table format
def print_wallet(wallet):
    table = "\nWallet\n"
    table += "-" * 65
    table += "\n|{:>4}| {:>8}| {:>8}| {:>15}| {:>12}| {:>6}|\n".format("Nr", "Type", "Symbol", "Volume", "Price", "Base")
    i = 1
    for key in wallet:
        res = wallet[key]
        table += ("|{:>4}| {:>8}| {:>8}| {:>15.8f}| {:>12.4f}| {:>6}|\n".format(i, res["type"], res["symbol"], res["volume"], res["price"], res["base"]))
        i += 1
    table += "-" * 65
    table += "\n"
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
    wallet = read_wallet()
    if wallet is None:
        print("Unable to read config file {0}".format(DEFAULT_CONFIG_PATH))
        return
    menu(wallet)


if __name__ == "__main__":
    main()
