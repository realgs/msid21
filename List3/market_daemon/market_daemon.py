import json
import os

from time import sleep
from typing import Optional, Callable, Any

from utils import print_decorator
import requests

OrderList = list[list[float]]

CONFIG_PATH: str = "config.json"

BASE_CURRENCY: str = "USD"
DEFAULT_ORDER_NUM: int = -1
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
    with open(path, 'r') as f:
        result = dict(json.load(f))
        return result


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
        config = load_config(config_path)["API"][api_identifier]
        discovered_fields = set([k for k in recursive_keys(config)])
        diff = REQUIRED_FIELDS - discovered_fields

        if diff:
            raise KeyError(f"API '{api_identifier}' config file doesn't contain required fields: {diff}.")

        return MarketDaemon(api_identifier, config["url"], config)

    @print_decorator
    def get_orders(self, instrument: str, base: str = BASE_CURRENCY, size: int = DEFAULT_ORDER_NUM):
        """Gets the orders for a given instrument and base currency, selects 'size' number of orders

        Args:
            instrument: Symbol of an instrument to look up in the orderbook
            base: Base currency
            size: Number of orders to return (-1 gives the full list of orders)

        Returns:
            Optional of Tuple of dicts containing float pairs representing prices and quantities of orders respectively.
            The first tuple represents buy offers and the second one - sell offers.
            None is returned if query fails.
        """
        response: requests.Response = self._make_request(instrument, base)
        if response:
            content = dict(response.json())
            try:
                buys = content[self._settings["bids"]]
                sells = content[self._settings["asks"]]
                buys, sells = self._normalize_response_contents(buys, sells)
                if not buys or not sells:
                    return None
                else:
                    return {order[0]: order[1] for order in buys}, {order[0]: order[1] for order in sells}
            except KeyError:
                print("Your request produced a response but no bids or asks were found")
                return None

    def stream(self, instrument: str, base: str = BASE_CURRENCY, timeout_sec: float = DEFAULT_TIMOUT, verbose=True):
        while True:
            buys, sells = self.get_orders(instrument, base, size=1)
            if verbose:
                print(buys, sells)
            yield buys, sells
            sleep(timeout_sec)

    @print_decorator
    def _make_request(self, instrument: str, base: str = BASE_CURRENCY) -> Optional[requests.Response]:
        try:
            response = requests.request("GET", self._to_request_url(instrument, base))
            if response.status_code in range(200, 300) and "code" not in dict(response.json()):
                return response
            else:
                print(f"Your request for '{instrument}{base}' at {self} didn't produce a valid response.")
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print(f"Your request for '{instrument}{base}' at {self} timed out, retrying in 5s...")
            sleep(5.0)
            self._make_request(instrument, base)
        except requests.exceptions.RequestException:
            print(f"Your request for '{instrument}{base}' at {self} failed")
            return None

    def _normalize_response_contents(self, buys, sells) -> tuple[OrderList, OrderList]:
        """Normalizes the contents of bids and asks to [price, quantity] format using orderbook_parser"""
        return self._orderbook_parser(buys), self._orderbook_parser(sells)

    @print_decorator
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

    def __str__(self):
        return f"{self.name}"


def price_diff(lhs: dict[float, float], rhs: dict[float, float]):
    diff = (list(lhs.keys())[0] - list(rhs.keys())[0]) / list(lhs.keys())[0]
    return diff * 100


def compare_stream(d1: MarketDaemon, d2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY, kind: str = "buy"):
    """Compares prices for a given instrument; kind == "buys" compares bid prices and "sell" compares ask prices"""
    while True:
        b1, s1 = d1.get_orders(instrument, base, size=1)
        b2, s2 = d2.get_orders(instrument, base, size=1)
        diff = price_diff(b1, b2) if kind == "buy" else (price_diff(s1, s2) if kind == "sell" else None)
        print(f"{d1} vs {d2} is {diff:.4f}% for {kind} of pair {instrument}{base}")
        yield diff
        sleep(DEFAULT_TIMOUT)


def compare_transfer_stream(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY):
    """Creates a generator tracking price differences as a percentage between buy market 'm1' and sell market 'm2'
    for a given instrument. Update frequency is constrained by a timeout.

    Args:
        m1: Buy market for given instrument
        m2: Sell market for given instrument
        instrument: Instrument intended to buy at m1 and sell at m2
        base: Base currency

    Returns:
        Price difference between buy at market m1 and sell at market m2 expressed as percentage.
        Negative percentage implies lack of profitability of arbitrage between markets m1, m2 for a given instrument.
    """
    while True:
        b1, s1 = m1.get_orders(instrument, base, size=1)
        b2, s2 = m2.get_orders(instrument, base, size=1)
        diff = price_diff(b1, s2)
        print(f"Buy at {m1}, sell at {m2} for {instrument}{base} - profitability = {diff:.4f}%")
        yield diff
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
        preferences = load_config(CONFIG_PATH)
    except KeyError:
        print("Preferences entries not found, using default values")
    except FileNotFoundError:
        decision = input("Config file not discovered. Would you like to create config? Y/n: ")
        if decision == "y" or decision == "Y" or decision == "\n":
            create_config()
        else:
            print("Using default settings")


_onload()
