from __future__ import annotations

import json
import os
import random
from datetime import datetime

from time import sleep
import pandas as pd
from typing import Optional, Callable, Any

import bcolors
import requests
from tqdm import tqdm

from market_daemon import optimizers, parsers

OrderList = list[tuple[float, float]]

CONFIG_PATH: str = "api_config.json"

BASE_CURRENCY: str = "USD"
DEFAULT_ORDER_NUM: int = 3
DEFAULT_TIMOUT: float = 5.0

SAMPLE_CONFIG: dict = {
    "API": {
        "default": {
            "url": "https://bitbay.net/API/Public",
            "orderbook_endpoint": "orderbook.json",
            "instrument_sep": "-",
            "asks": "asks",
            "bids": "bids",
            "taker_fee": 0.001,
            "transfer_fee": {
                "BTC": 0.0005,
                "ETH": 0.01,
                "XLM": 0.005
            }
        }
    },
    "preferences": {
        "base_currency": "USD",
        "default_timout": 5.0,
        "default_order_num": 5
    }
}


def load_config(path="api_config.json"):
    try:
        with open(path, 'r') as f:
            result = dict(json.load(f))
            return result
    except json.decoder.JSONDecodeError:
        return dict()


def recursive_keys(dictionary: dict):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield key
            yield from recursive_keys(value)
        else:
            yield key


REQUIRED_FIELDS: set[str] = {"url", "orderbook_endpoint", "instrument_sep",
                             "asks", "bids", "taker_fee", "transfer_fee"}


class MarketDaemon:
    def __init__(self, name: str, url: str, settings: dict):
        self.name = name
        self.url = url

        self._settings = settings
        self._transfer_fees = None

        if "currencies_url" in self._settings:
            self._transfer_fees = self._load_transfer_fees(self._settings["currencies_url"])
        else:
            self._transfer_fees = self._settings["transfer_fee"]

        self._orderbook_parser: Callable[[list], OrderList] = lambda x: x
        self._market_parser: Callable[[requests.Response], set[str]] = lambda x: set()

        if self.name == "bittrex":
            self.market_parser = parsers.bittrex_request_to_pairs
            self.orderbook_parser = parsers.bittrex_parser
        elif self.name == "bitbay":
            self.market_parser = parsers.bitbay_request_to_pairs

        self._available_pairs_estimate = self._get_available_pairs(self.market_parser)

    @staticmethod
    def build_from_config(api_identifier: str, config_path: str = "api_config.json"):
        """Builds a MarketDaemon with a given identifier from specified api_config.json file
        Args:
            api_identifier: name of the API for which config is provided
            config_path: relative path to config file
        Returns:
            Constructed MarketDaemon instance provided that the config file was valid
        Raises:
            FileNotFoundError: if file under config_path is unreachable
            KeyError: if the parser couldn't find required entry in config for given api_identifier
        """
        conf_file = load_config(config_path)
        if not conf_file:
            raise KeyError(f"Error in reading {config_path} file")

        config = conf_file["API"][api_identifier]
        discovered_fields = set([k for k in recursive_keys(config)])
        diff = REQUIRED_FIELDS - discovered_fields

        if diff:
            raise KeyError(f"API '{api_identifier}' config file doesn't contain required fields: {diff}.")

        return MarketDaemon(api_identifier, config["url"], config)

    def get_orders(self, instrument: str, base: str = BASE_CURRENCY, size: int = DEFAULT_ORDER_NUM,
                   verbose: bool = True, raw: bool = False):
        """Gets the orders for a given instrument and base currency, selects 'size' number of orders
        Args:
            instrument: Symbol of an instrument to look up in the orderbook
            base: Base currency
            size: Number of orders to return (-1 gives the full list of orders)
            verbose: prints the results if set to True
            raw: returns list of tuples [(price, qty)... ] instead
        Returns:
            Optional of Tuple of dicts containing float pairs representing prices and quantities of orders respectively.
            The first tuple represents asks or buy offers and the second one - bids or sell offers. None is
            returned if query fails.
        """
        response: requests.Response = self._make_request(self._to_request_url(instrument, base), verbose=verbose)
        if response:
            content = dict(response.json())
            try:
                buys = content[self._settings["asks"]]
                sells = content[self._settings["bids"]][:size]

                if size != -1:
                    buys = buys[:size]
                    sells = sells[:size]

                buys, sells = self._normalize_response_contents(buys, sells)
                if not buys or not sells:
                    return None
                else:
                    if raw:
                        return buys, sells
                    else:
                        result = {order[0]: order[1] for order in buys}, {order[0]: order[1] for order in sells}
                        if verbose:
                            self._print_orders(result[1], instrument, base, kind="sell")
                            self._print_orders(result[0], instrument, base, kind="buy")
                        return result
            except KeyError:
                if verbose:
                    print("Your request produced a response but no bids or asks were found")
                return None

    def stream(self, instrument: str, base: str = BASE_CURRENCY, timeout_sec: float = DEFAULT_TIMOUT, verbose=True):
        while True:
            buys, sells = self.get_orders(instrument, base, size=1)
            if verbose:
                print(buys, sells)
            yield buys, sells
            sleep(timeout_sec)

    def order_value(self, price: float, quantity: float, instrument: str, kind: str = "buy"):
        """Returns total price of fulfilling (taking) an order including taker fees if they are provided
        If not returns bare value of the order. Kind can take values 'buy' or 'sell'"""
        try:
            total = price * quantity
            return total * (1 + self._settings["taker_fee"] * (1 if kind == "buy" else -1 if kind == "sell" else 0))
        except KeyError:
            print(f"Settings for market {self} do not have information about taker_fee "
                  f"for {instrument}. Returning bare order value.")
            return price * quantity

    def valuation(self, instrument: str, quantity: float, base: str = BASE_CURRENCY):
        to_sell = quantity
        profit = 0.0

        symbol = f"{instrument}{self.settings['instrument_sep']}{base}"

        if symbol not in self._available_pairs_estimate:
            return 0.0
        else:
            _, sells = self.get_orders(instrument, base, -1, verbose=False, raw=True)

            try:
                i = 0
                while to_sell > 0.0:
                    price = sells[i][0]
                    volume = sells[i][1]

                    sell_quantity = min(to_sell, volume)
                    to_sell -= sell_quantity
                    sells[i][1] -= sell_quantity

                    profit += price * sell_quantity

                    if sells[i][1] <= 0.0:
                        i += 1

                return profit
            except IndexError:
                print(f"W Could not sell total amount of product due to market saturation")
                return profit
            except KeyError:
                print(f"W could not fetch {instrument} from API {self}")
                return 0.0

    def _make_request(self, url: str, verbose: bool = True) -> Optional[requests.Response]:
        try:
            response = requests.request("GET", url)
            if response.status_code in range(200, 300):
                return response
            else:
                if verbose:
                    print(f"Your request @ '{url}' at {self} didn't produce a valid response.")
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if verbose:
                print(f"Your request @ '{url}' at {self} timed out, retrying in {DEFAULT_TIMOUT}s...")
            sleep(DEFAULT_TIMOUT)
            self._make_request(url)
        except requests.exceptions.RequestException:
            if verbose:
                print(f"Your request @ '{url}' at {self} failed")
            return None

    def _load_transfer_fees(self, currencies_url: str):
        try:
            response = self._make_request(currencies_url)
            result: dict[str, float] = dict()

            data = list(response.json())
            for e in data:
                result[e["symbol"]] = float(e["txFee"])
            return result
        except KeyError:
            return None

    def _get_available_pairs(self, request_to_pairs: Callable[[requests.Response], set[str]]) -> set[str]:
        """Returns list of pairs as strings as per request_to_pairs parser provided by the user
        If no parser is set, empty set is returned"""
        response = self._make_request(self.settings["markets_url"])
        if response:
            return request_to_pairs(response)
        else:
            return set()

    def _normalize_response_contents(self, buys, sells) -> tuple[OrderList, OrderList]:
        """Normalizes the contents of bids and asks to [price, quantity] format using orderbook_parser"""
        return self._orderbook_parser(buys), self._orderbook_parser(sells)

    def _to_request_url_pair(self, pair_str: str):
        return f"{self.url}/{pair_str}/{self._settings['orderbook_endpoint']}"

    def _to_request_url(self, instrument: str, base: str = BASE_CURRENCY) -> str:
        return f"{self.url}/{instrument}{self._settings['instrument_sep']}{base}/{self._settings['orderbook_endpoint']}"

    def transfer_fee(self, instrument: str, verbose=True):
        """Returns the transfer fee for a given security,
        if information in settings has not been provided 0 is returned"""
        if instrument in self._transfer_fees:
            return self._transfer_fees[instrument]
        else:
            if verbose:
                print(bcolors.WARN + f"W: returned transfer fee = 0 for {instrument} @ market {self}" + bcolors.ENDC)
            return 0

    def get_joint_pairs(self, other: MarketDaemon):
        """Returns the common set of pairs at two market daemons"""
        self_pairs = self._get_available_pairs(self.market_parser)
        other_pairs = other._get_available_pairs(other.market_parser)

        return self_pairs.intersection(other_pairs)

    @property
    def settings(self):
        # Getter only property
        return self._settings

    @property
    def orderbook_parser(self):
        return self._orderbook_parser

    @orderbook_parser.setter
    def orderbook_parser(self, parser: Callable[[Any], OrderList]):
        """Sets a parser for converting orderbook prices into standard form [[price, quantity]..]
        Sample parsers are provided in market_daemon.parsers
        Args:
            parser: A function of signature: Any -> list[list[float]] intended to transform bids / asks response
            into standardized form. Example valid conversion:
        Examples:
            Original: [{quantity: 1.566870, price: 27884.34}, {quantity: 0.9982, price: 27892.88}]
            After transform: [[27884.34, 1.566870], [27892.88, 0.9982]]
        """
        self._orderbook_parser = parser

    @property
    def market_parser(self):
        return self._market_parser

    @market_parser.setter
    def market_parser(self, parser: Callable[[requests.Response], set[str]]):
        self._market_parser = parser

    def _print_orders(self, orders: dict[float, float], instrument: str, base: str, kind: str = "buy"):
        if orders:
            for price, qty in orders.items():
                print(f"[{self}] {kind.capitalize()} {qty}{instrument} at {price} {instrument}{base}")

    def __str__(self):
        return f"{self.name}"


def price_diff(lhs: dict[float, float], rhs: dict[float, float]):
    diff = (list(lhs.keys())[0] - list(rhs.keys())[0]) / list(lhs.keys())[0]
    return diff * 100


def compare_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                   kind: str = "buy", verbose: bool = True):
    """Creates a generator comparing buy, sell or transfer prices for a given instrument at two markets m1, m2.
    Update frequency is constrained by a timeout.
    Args:
        m1: MarketDaemon monitoring market 1
        m2: MarketDaemon monitoring market 2
        instrument: Symbol for an instrument to query
        base: Base currency
        kind: 'buy' for comparing buy prices, 'sell' for comparing sell prices, 'transfer' for transfer stream
        verbose: prints the results if set to True
    Returns:
        Price difference between buy or sell between markets m1, m2.
        Positive percentage implies the price is lower at market m2, negative implies the contrary.
        Transfer operation is profitable iff the return percentage difference is negative
    """
    while True:
        b1, s1 = m1.get_orders(instrument, base, size=1, verbose=verbose)
        b2, s2 = m2.get_orders(instrument, base, size=1, verbose=verbose)

        if kind == "buy":
            diff = price_diff(b1, b2)
        elif kind == "sell":
            diff = price_diff(s1, s2)
        elif kind == "transfer":
            diff = price_diff(b1, s1)
        else:
            diff = None

        if verbose:
            print(f"{m1} vs {m2} is {diff:.4f}% for {kind} of pair {instrument}{base}\n")
        yield diff
        sleep(DEFAULT_TIMOUT)


def iterative_arbitrage(to_buy, to_sell, instrument, base, m1, m2, verbose=True):
    profit = 0.0
    volume = 0.0
    total_buy = 0.0

    transfer_paid_number = 0
    order_num = 0

    transfer_to_pay = m1.transfer_fee(instrument, verbose=verbose)

    while to_buy and to_sell and to_buy[0][0] < to_sell[0][0]:
        buy_qty = min(to_buy[0][1], to_sell[0][1])
        sell_qty = buy_qty

        order_num += 1

        if transfer_to_pay > 0.0:
            if transfer_to_pay < sell_qty:
                sell_qty -= transfer_to_pay
                transfer_to_pay = 0.0
                transfer_paid_number = order_num
            else:
                transfer_to_pay -= sell_qty
                sell_qty = 0.0

        buy_value = m1.order_value(to_buy[0][0], buy_qty, instrument)
        sell_value = m2.order_value(to_sell[0][0], sell_qty, instrument, kind="sell")

        consider_negative_profit: bool = transfer_to_pay > 0.0 or (transfer_to_pay == 0.0 and
                                                                   transfer_paid_number == order_num)

        if buy_value < sell_value or consider_negative_profit:
            if consider_negative_profit and verbose:
                print("\tConsidering negative profit...")

            volume += buy_qty
            total_buy += buy_value
            profit += sell_value - buy_value

            if verbose:
                print(f"\tBuy {buy_qty} {instrument} at market {m1} for {to_buy[0][0]} {instrument}{base}")
                print(f"\tSell {sell_qty} {instrument} at market {m2} for {to_sell[0][0]} {instrument}{base}")
                print(f"\tTotal profit on order: {sell_value} {base} - {buy_value} {base} ="
                      f" {sell_value - buy_value} {base}\n")
            if to_buy[0][1] < to_sell[0][1]:
                del to_buy[0]
                to_sell[0][1] -= sell_qty
            else:
                del to_sell[0]
                to_buy[0][1] -= buy_qty
        else:
            break

    profitability = 100 * profit / total_buy if total_buy else 0.0

    return profit, profitability


def arbitrage_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                     solver=optimizers.LinprogArbitrage(), verbose: bool = True):
    """
    Creates a generator for monitoring arbitrage opportunity for buy at market m1 and sell at m2 of a given symbol
    Fees are taken into account if relevant entries are present in config

    Args:
        m1: Buy market for given instrument
        m2: Sell market for given instrument
        instrument: Instrument intended to buy at m1 and sell at m2
        base: Base currency
        solver: an instance of optimizers.ArbitrageOptimizer or None for iterative method
        verbose: prints the results if set to True


    Yields:
        Tuple: profit, profitability of arbitrage between m1 and m2

    Raises:
        StopIteration: when the stream couldn't be established after max_retries as stated in the config file
    """
    while True:
        try:
            to_buy, _ = m1.get_orders(instrument, base, size=-1, verbose=False, raw=True)
            _, to_sell = m2.get_orders(instrument, base, size=-1, verbose=False, raw=True)

            if isinstance(solver, optimizers.ArbitrageOptimizer):
                profit, profitability, _ = solver(to_buy, to_sell,
                                                  (m1.settings["taker_fee"], m2.settings["taker_fee"]),
                                                  m1.transfer_fee(instrument), verbose=False)
            else:
                profit, profitability = iterative_arbitrage(to_buy, to_sell, instrument, base, m1, m2, verbose)

            if profit <= 0.0:
                if verbose:
                    print(bcolors.FAIL + f"No orders were found to be profitable for buy of {instrument}"
                                         f" at {m1} and sell at {m2}" + bcolors.ENDC)
                yield 0.0, 0.0
            else:
                if verbose:
                    print(bcolors.OK + f"{m1} -> {m2}: profit = {profit} {base},"
                                       f" profitability = {profitability:.4f}%\n" + bcolors.ENDC)

                yield profit, profitability
        except TypeError:
            print(f"Cannot fetch {instrument}{base}")
            yield 0.0, 0.0

        sleep(DEFAULT_TIMOUT)


def check_3_random_pairs(src: MarketDaemon, dest: MarketDaemon):
    """Returns a dataframe with pairs columns denoting the 3 pairs, and profit column expressed in base currency
    of each pair, profit is 0 if no arbitrage opportunity is present"""
    intersecting_pairs: set[str] = src.get_joint_pairs(dest)
    pairs = random.sample(list(intersecting_pairs), 3)

    data = {"pair": pairs, "profit": [], "profitability": []}

    print("Checking pairs...")

    for pair in tqdm(pairs):
        ss = arbitrage_stream(src, dest, *pair.split("-"), verbose=False, solver=optimizers.LinprogArbitrage())
        profit, profitability = next(ss)
        data["profit"].append(profit)
        data["profitability"].append(profitability)

    df = pd.DataFrame(data)
    return df.sort_values(by="profitability", ascending=False)


def arbitrage_summary(src: MarketDaemon, dest: MarketDaemon, filter_base: list[str] = None,
                      solver=optimizers.LinprogArbitrage()):
    """Returns a dataframe containing pairs available at both src and dest markets and profits of
     arbitrage opportunities expressed in base currency"""
    joint_pairs = src.get_joint_pairs(dest)
    data = {"pair": [], "instrument": [], "base": [], "profitBase": [], "profitability": [], "srcMarket": [],
            "destMarket": [], "txFeeBase": [], "time": []}

    if filter_base:
        joint_pairs = [p for p in joint_pairs if p.split("-")[1] in filter_base]

    print("Processing joint pairs...")
    for pair in tqdm(joint_pairs):
        instrument, base = pair.split(src.settings["instrument_sep"])
        ss = arbitrage_stream(src, dest, instrument, base, verbose=False, solver=solver)
        data["pair"].append(pair)
        data["instrument"].append(instrument)
        data["base"].append(base)
        profit, profitability = next(ss)
        data["profitBase"].append(profit)
        data["profitability"].append(profitability)
        data["srcMarket"] = str(src)
        data["destMarket"] = str(dest)
        data["txFeeBase"].append(src.transfer_fee(instrument, verbose=False))
        data["time"].append(datetime.now())

    df = pd.DataFrame(data)
    df = df.sort_values(by="profitability", ascending=False)
    return df


def create_config():
    if os.path.isfile(CONFIG_PATH):
        print(bcolors.WARN + "W Config is already present, no modifications were made." + bcolors.ENDC)
    else:
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(SAMPLE_CONFIG, f)
                print("Sample config created")
        except IOError:
            print("Config file not accessible")


def _onload():
    try:
        config = load_config(CONFIG_PATH)
        preferences = config["preferences"]

        global DEFAULT_TIMOUT, DEFAULT_ORDER_NUM, BASE_CURRENCY
        DEFAULT_TIMOUT = preferences["default_timout"]
        DEFAULT_ORDER_NUM = preferences["default_order_num"]
        BASE_CURRENCY = preferences["base_currency"]

        pd.set_option('display.max_colwidth', None)

        print(bcolors.OK + "User preferences loaded successfully\n" + bcolors.ENDC)
    except KeyError:
        print(bcolors.WARN + "W Some of the preferences couldn't been set, using default values" + bcolors.ENDC)
    except FileNotFoundError:
        decision = input("Config file not discovered. Would you like to create config? Y/n: ")
        if decision == "y" or decision == "Y" or decision == "\n":
            create_config()
        else:
            print("I Using default settings")


_onload()
