import requests
from time import sleep

API = "https://bitbay.net/API/Public/"
BASE_CURRENCY = "USD"
INSTRUMENTS = ["BTC", "ETH", "XLM"]
TIMEOUT_SEC = 5.0
DEFAULT_ORDER_NUM = 3


def make_request(url):
    response = requests.get(url)
    if response.status_code not in range(200, 300):
        print(f"Request for {url} failed")
        return None
    else:
        return response


def get_orders(instrument, base=BASE_CURRENCY, size=3):
    content = make_request(f"{API}{instrument}{base}/orderbook.json").json()
    try:
        buys = dict(content["bids"][:size])
        sells = dict(content["asks"][:size])
        return buys, sells
    except KeyError:
        print(f"Your request for {instrument}{base} failed to produce a valid response")
        return {1.0: -1.0}, {1.0: -1.0}


def print_orders(orders, instrument, base=BASE_CURRENCY):
    print(f"\nInstrument: {instrument}{base}")
    buys, sells = orders
    print("Buy orders:")
    for price, amount in buys.items():
        print(f"\t{amount}{instrument} for {price * amount}{base} @ {instrument}{base} = {price}")
    print("Sell orders:")
    for price, amount in sells.items():
        print(f"\t{amount}{instrument} for {price * amount}{base} @ {instrument}{base} = {price}")


def print_pair(instrument, base=BASE_CURRENCY, size=DEFAULT_ORDER_NUM):
    print_orders(get_orders(instrument, base, size), instrument, base)


def get_price_diff(instrument, base=BASE_CURRENCY):
    buys, sells = get_orders(instrument, base, size=1)
    diff = 1 - ((list(sells.keys())[0] - list(buys.keys())[0]) / list(buys.keys())[0])
    return diff


def price_diff_stream(instrument, base=BASE_CURRENCY, timeout=TIMEOUT_SEC):
    while True:
        yield get_price_diff(instrument, base)
        sleep(timeout)


# Zad 1 (5 pkt)
def ex1():
    for i in INSTRUMENTS:
        print_pair(i)


# Zad 2 (5 pkt)
def ex2():
    pds = price_diff_stream("BTC")
    for _ in range(3):
        print(next(pds))


if __name__ == "__main__":
    ex1()
    ex2()
