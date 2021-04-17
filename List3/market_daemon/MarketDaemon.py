import json

from time import sleep
from typing import Optional, Callable, Any

from utils import print_decorator
import requests

INSTRUMENTS = ["BTC", "ETH", "XLM"]
BASE_CURRENCY = "USD"
DEFAULT_ORDER_NUM = -1
DEFAULT_TIMOUT = 5.0

OrderList = list[list[float]]


def bittrex_parser(content: list[dict[str, str]]) -> OrderList:
    """
    Converts bittrex ask and bid response contents to [[price, quantity], ...] format
    Raises:
        ValueError: if parser cannot interpret content parameter correctly
    """
    result = []
    try:
        for d in content:
            result.append([float(d["rate"]), float(d["quantity"])])
        return result
    except KeyError:
        raise ValueError("Couldn't parse content: no rate or quantity elements found")


APIS = {
    "bitbay": {
        "url": "https://bitbay.net/API/Public",
        "endpoint": "orderbook.json",
        "taker_fee": 0.001,
        "transfer_fee": {
            "BTC": 0.0005,
            "ETH": 0.01,
            "XLM": 0.005
        }
    },
    "bittrex": {
        "url": "https://api.bittrex.com/v3/markets",
        "endpoint": "orderbook",
        "taker_fee": 0.0075,
        "transfer_fee": {
            "BTC": 0.0003,
            "ETH": 0.0085,
            "XLM": 0.05
        }
    }
}

REQUIRED_FIELDS: set[str] = {"url", "orderbook_endpoint", "instrument_sep",
                             "asks", "bids", "taker_fee", "transfer_fee"}


def recursive_keys(dictionary: dict):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield key
            yield from recursive_keys(value)
        else:
            yield key


class MarketDaemon:
    def __init__(self, name: str, url: str, settings: dict):
        self.name = name
        self.url = url

        self._settings = settings

        self._orderbook_parser: Callable[[list], OrderList] = lambda x: x

    @staticmethod
    def build_from_config(api_identifier: str, config_path: str = "..\\config.json"):
        """Builds a MarketDaemon with a given identifier from specified config.json file

        Args:
            api_identifier: name of the API for which config is provided
            config_path: relative path to config file

        Returns:
            Constructed MarketDaemon instance provided that the config file was valid

        Raises:
            KeyError: if the parser couldn't find required entry in config for given api_identifier
        """
        config = load_config(config_path)["API"][api_identifier]
        discovered_fields = set([k for k in recursive_keys(config)])
        diff = REQUIRED_FIELDS - discovered_fields

        if diff:
            raise KeyError(f"API {api_identifier} config file doesn't contain required fields: {diff}.")

        return MarketDaemon(api_identifier, config["url"], config)

    @print_decorator
    def get_orders(self, instrument: str, base: str = BASE_CURRENCY, size: int = DEFAULT_ORDER_NUM):
        response: requests.Response = self._make_request(instrument, base)
        if response:
            content = dict(response.json())
            try:
                buys = content[self._settings["bids"]]
                sells = content[self._settings["asks"]]
                buys, sells = self._normalize_response_contents(buys, sells)
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

    def set_parser(self, parser: Callable[[Any], OrderList]):
        """Sets the orderbook parser if a custom one is needed"""
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


def compare_transfer_stream(d1: MarketDaemon, d2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY):
    """
    Args:
        d1: Buy market for given instrument
        d2: Sell market for given instrument
        instrument: Instrument intended to buy at d1 and sell at d2
        base: Base currency

    Returns:
        Price difference between buy at market d1 and sell at market d2 expressed as percentage.
        Negative percentage implies lack of profitability of arbitrage between markets d1, d2 for a given instrument.
    """
    while True:
        b1, s1 = d1.get_orders(instrument, base, size=1)
        b2, s2 = d2.get_orders(instrument, base, size=1)
        diff = price_diff(b1, s2)
        print(f"Buy at {d1}, sell at {d2} for {instrument}{base} - profitability = {diff:.4f}%")
        yield diff
        sleep(DEFAULT_TIMOUT)


@print_decorator
def load_config(path="..\\config.json"):
    with open(path, 'r') as f:
        result = dict(json.load(f))
        return result


def main():
    bitbay = MarketDaemon.build_from_config("bitbay")

    bittrex = MarketDaemon.build_from_config("bittrex")
    bittrex.set_parser(bittrex_parser)

    """
    bitbay = MarketDaemon("bitbay", APIS["bitbay"]["url"], APIS["bitbay"]["endpoint"],
                          taker_fee=APIS["bitbay"]["taker_fee"], transfer_fees=APIS["bitbay"]["transfer_fee"])

    bittrex = MarketDaemon("bittrex", APIS["bittrex"]["url"], APIS["bittrex"]["endpoint"],
                           taker_fee=APIS["bittrex"]["taker_fee"], transfer_fees=APIS["bittrex"]["transfer_fee"])
    bittrex.set_parser(bittrex_parser)
    """

    bitbay.get_orders("BTC")
    bittrex.get_orders("ETH")

    css = compare_transfer_stream(bitbay, bittrex, "BTC")
    for _ in range(5):
        next(css)

    cs = compare_stream(bitbay, bittrex, "BTC")
    for _ in range(5):
        next(cs)


if __name__ == "__main__":
    main()
