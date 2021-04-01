from typing import Optional

import requests
from time import sleep

API = "https://bitbay.net/API/Public/"
BASE_CURRENCY = "USD"
INSTRUMENTS = ["BTC", "ETH", "LTC"]
INTERVAL = 5
BASE_LIMIT = 20
FIND_AVERAGE_PROFIT = False


def make_request(url: str) -> Optional[requests.Response]:
    response = requests.get(url)
    if response.status_code not in range(200, 300):
        print(f"Request for {url} failed")
        return None
    else:
        return response


def get_orders(instrument: str, base: str = BASE_CURRENCY, size: int = 3) -> tuple[dict[float, float],
                                                                                   dict[float, float]]:
    content = make_request(f"{API}{instrument}{base}/orderbook.json").json()
    try:
        buys = dict(content["bids"][:size])
        sells = dict(content["asks"][:size])
        return buys, sells
    except KeyError:
        print(f"Your request for {instrument}{base} failed to produce a valid response")
        return {0.0: 0.0}, {0.0: 0.0}


def print_orders(orders: tuple[dict[float, float], dict[float, float]], instrument: str, base: str = BASE_CURRENCY):
    print(f"Instrument: {instrument}{base}")
    buys, sells = orders
    print("Buy orders:")
    for price, amount in buys.items():
        print(f"\t{amount}{instrument} for {price * amount}{base} @ {instrument}{base} = {price}")
    print("Sell orders:")
    for price, amount in sells.items():
        print(f"\t{amount}{instrument} for {price * amount}{base} @ {instrument}{base} = {price}")


def print_pair(instrument: str, base: str = BASE_CURRENCY, size: int = 3):
    print_orders(get_orders(instrument, base, size), instrument, base)


def get_price_diff(instrument: str, base: str = BASE_CURRENCY) -> float:
    buys, sells = get_orders(instrument, base, size=1)
    diff = 1 - ((list(sells.keys())[0] - list(buys.keys())[0]) / list(buys.keys())[0])
    return diff


def price_diff_stream(instrument: str, base: str = BASE_CURRENCY, timeout: float = 5.0):
    while True:
        yield get_price_diff(instrument, base)
        sleep(timeout)


def ex1():
    for i in INSTRUMENTS:
        print_pair(i)


def ex2():
    pds = price_diff_stream("BTC")
    for _ in range(10):
        print(next(pds))


if __name__ == "__main__":
    ex1()
    ex2()
