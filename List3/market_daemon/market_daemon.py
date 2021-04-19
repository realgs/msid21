import json
import os

from time import sleep
from typing import Optional, Callable, Any

import requests

OrderList = list[list[float]]

CONFIG_PATH: str = "config.json"

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


def load_config(path="config.json"):
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

        self._orderbook_parser: Callable[[list], OrderList] = lambda x: x

    @staticmethod
    def build_from_config(api_identifier: str, config_path: str = "config.json"):
        """Builds a MarketDaemon with a given identifier from specified config.json file

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
                   verbose: bool = True):
        """Gets the orders for a given instrument and base currency, selects 'size' number of orders

        Args:
            instrument: Symbol of an instrument to look up in the orderbook
            base: Base currency
            size: Number of orders to return (-1 gives the full list of orders)
            verbose: prints the results if set to True

        Returns:
            Optional of Tuple of dicts containing float pairs representing prices and quantities of orders respectively.
            The first tuple represents asks or buy offers and the second one - bids or sell offers. None is
            returned if query fails.
        """
        response: requests.Response = self._make_request(instrument, base, verbose=verbose)
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
            print(f"Settings for market {self} do not have information about taker_fee or transfer_fee "
                  f"for {instrument}. Returning bare order value.")
            return price * quantity

    def _make_request(self, instrument: str, base: str = BASE_CURRENCY,
                      verbose: bool = True) -> Optional[requests.Response]:
        try:
            response = requests.request("GET", self._to_request_url(instrument, base))
            if response.status_code in range(200, 300) and "code" not in dict(response.json()):
                return response
            else:
                if verbose:
                    print(f"Your request for '{instrument}{base}' at {self} didn't produce a valid response.")
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if verbose:
                print(f"Your request for '{instrument}{base}' at {self} timed out, retrying in {DEFAULT_TIMOUT}s...")
            sleep(DEFAULT_TIMOUT)
            self._make_request(instrument, base)
        except requests.exceptions.RequestException:
            if verbose:
                print(f"Your request for '{instrument}{base}' at {self} failed")
            return None

    def _normalize_response_contents(self, buys, sells) -> tuple[OrderList, OrderList]:
        """Normalizes the contents of bids and asks to [price, quantity] format using orderbook_parser"""
        return self._orderbook_parser(buys), self._orderbook_parser(sells)

    def _to_request_url(self, instrument: str, base: str = BASE_CURRENCY) -> str:
        return f"{self.url}/{instrument}{self._settings['instrument_sep']}{base}/{self._settings['orderbook_endpoint']}"

    def set_parser(self, parser: Callable[[Any], OrderList]) -> None:
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

    def get_parser(self) -> Callable[[Any], OrderList]:
        return self._orderbook_parser

    def transfer_fee(self, instrument: str):
        """Returns the transfer fee for a given security,
        if information in settings has not been provided 0 is returned"""
        if instrument in self._settings["transfer_fee"]:
            return self._settings["transfer_fee"][instrument]
        else:
            return 0

    @property
    def settings(self):
        # Getter only property
        return self._settings

    def _print_orders(self, orders: dict[float, float], instrument: str, base: str, kind: str = "buy"):
        if orders:
            for price, qty in orders.items():
                print(f"[{self}] {kind.capitalize()} {qty}{instrument} at {price} {instrument}{base}")

    def __str__(self):
        return f"{self.name}"


def price_diff(lhs: dict[float, float], rhs: dict[float, float]):
    diff = (list(lhs.keys())[0] - list(rhs.keys())[0]) / list(lhs.keys())[0]
    return diff * 100


# Zad 1 a-b (5 pkt)
def compare_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                   kind: str = "buy", verbose: bool = True):
    """Creates a generator comparing buy or sell prices for a given instrument at two markets m1, m2.
    Update frequency is constrained by a timeout.

    Args:
        m1: MarketDaemon monitoring market 1
        m2: MarketDaemon monitoring market 2
        instrument: Symbol for an instrument to query
        base: Base currency
        kind: 'buy' for comparing buy prices, 'sell' for comparing sell prices
        verbose: prints the results if set to True

    Returns:
        Price difference between buy or sell between markets m1, m2.
        Positive percentage implies the price is lower at market m2, negative implies the contrary.
    """
    while True:
        b1, s1 = m1.get_orders(instrument, base, size=1, verbose=verbose)
        b2, s2 = m2.get_orders(instrument, base, size=1, verbose=verbose)
        diff = price_diff(b1, b2) if kind == "buy" else (price_diff(s1, s2) if kind == "sell" else None)
        if verbose:
            print(f"{m1} vs {m2} is {diff:.4f}% for {kind} of pair {instrument}{base}\n")
        yield diff
        sleep(DEFAULT_TIMOUT)


# Zad 1 c
def compare_transfer_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                            verbose: bool = True):
    """Creates a generator tracking price differences as a percentage between buy market 'm1' and sell market 'm2'
    for a given instrument. Does not take fees into account. Update frequency is constrained by a timeout.

    Args:
        m1: Buy market for given instrument
        m2: Sell market for given instrument
        instrument: Instrument intended to buy at m1 and sell at m2
        base: Base currency
        verbose: prints the results if set to True

    Returns:
        Price difference between buy at market m1 and sell at market m2 expressed as percentage.
        Negative percentage implies lack of profitability of arbitrage between markets m1, m2 for a given instrument.
    """
    while True:
        b1, s1 = m1.get_orders(instrument, base, size=1, verbose=verbose)
        b2, s2 = m2.get_orders(instrument, base, size=1, verbose=verbose)
        diff = price_diff(b1, s2)
        if verbose:
            print(f"Buy at {m1}, sell at {m2} for {instrument}{base} - profitability = {-diff:.4f}%\n")
        yield diff
        sleep(DEFAULT_TIMOUT)


# Zad 2 (5 pkt)
def arbitrage_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                     verbose: bool = True):
    """Creates a generator for monitoring arbitrage opportunity for buy at market m1 and sell at m2 of a given symbol
    Fees are taken into account if relevant entries are present in config

    Args:
        m1: Buy market for given instrument
        m2: Sell market for given instrument
        instrument: Instrument intended to buy at m1 and sell at m2
        base: Base currency
        verbose: prints the results if set to True

    Returns:
        Profit if arbitrage opportunity exists, expressed in base currency, 0.0 otherwise

    Raises:
        StopIteration: when the stream couldn't be established after max_retries as stated in the config file
    """
    while True:
        try:
            b1, s1 = m1.get_orders(instrument, base, size=-1, verbose=False)
            b2, s2 = m2.get_orders(instrument, base, size=-1, verbose=False)

            if verbose:
                print(f"Analyzing query for {instrument}{base}:")
                print(b1)
                print(s2)

            to_buy = [[price, qty] for price, qty in b1.items()]
            to_sell = [[price, qty] for price, qty in s2.items()]

            profit = 0.0
            volume = 0.0
            total_buy = 0.0

            transfer_paid_number = 0
            order_num = 0

            transfer_to_pay = m1.transfer_fee(instrument)

            while to_buy and to_sell and to_buy[0][0] < to_sell[0][0]:
                buy_qty = min(to_buy[0][1], to_sell[0][1])
                sell_qty = buy_qty

                order_num += 1

                if transfer_to_pay > 0.0:
                    if transfer_to_pay < sell_qty:
                        sell_qty -= transfer_to_pay
                        transfer_to_pay = 0
                        transfer_paid_number = order_num
                    else:
                        transfer_to_pay -= buy_qty
                        sell_qty = 0

                """
                if not transfer_fee_paid:
                    sell_qty -= m1.transfer_fee(instrument)
                    transfer_fee_paid = True
                """

                buy_value = m1.order_value(to_buy[0][0], buy_qty, instrument)
                sell_value = m2.order_value(to_sell[0][0], sell_qty, instrument, kind="sell")

                if buy_value < sell_value:
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
                    if transfer_to_pay == 0.0 and transfer_paid_number == order_num:
                        if verbose:
                            print("\tConsidering negative profit : %s\n" % (sell_value - buy_value))
                        volume += buy_qty
                        total_buy += buy_value
                        profit += sell_value - buy_value
                        if to_buy[0][1] < to_sell[0][1]:
                            del to_buy[0]
                            to_sell[0][1] -= sell_qty
                        else:
                            del to_sell[0]
                            to_buy[0][1] -= buy_qty
                    else:
                        break

            if profit <= 0.0:
                if verbose:
                    print(f"No orders were found to be profitable for buy of {instrument} at {m1} and sell at {m2}")
                yield 0.0
            else:
                profitability = 100 * profit / total_buy if total_buy else 0.0
                print(f"Total volume: {volume}, total value: {total_buy} {base}, profit: {profit} {base},"
                      f"profitability: {profitability:.4f}%\n")

                yield profit

            sleep(DEFAULT_TIMOUT)
        except TypeError:
            if verbose:
                print(f"Connection to market was established but arbitrage stream couldn't interpret response data for"
                      f" {instrument}{base} at markets {m1}, {m2}")
                print(f"Retrying in {DEFAULT_TIMOUT} sec")

            yield 0.0
            sleep(DEFAULT_TIMOUT)


def create_config():
    if os.path.isfile(CONFIG_PATH):
        print("Config is already present, no modifications were made.")
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

        print("User preferences loaded successfully\n")
    except KeyError:
        print("Some of the preferences couldn't been set, using default values")
    except FileNotFoundError:
        decision = input("Config file not discovered. Would you like to create config? Y/n: ")
        if decision == "y" or decision == "Y" or decision == "\n":
            create_config()
        else:
            print("Using default settings")


_onload()
