import requests
import time
from enum import Enum
from texttable import Texttable


class Operation(Enum):
    BUY = "bids"
    SELL = "asks"


class Cryptocurrency(Enum):
    BTC = "BTC"
    LTC = "LTC"
    DASH = "DASH"


class Currency(Enum):
    USD = "USD"


def main():
    task1()
    task2()


def task1():
    for c in Cryptocurrency:
        response = make_request(c, Currency.USD)
        if response:
            print_orders(response.json(), Operation.BUY, c, Currency.USD)
            print_orders(response.json(), Operation.SELL, c, Currency.USD)
        else:
            print(f"Error {response.status_code} for {c.value}/USD request!")


def make_request(cryptocurrency: Cryptocurrency, currency: Currency):
    cryptocurrency = cryptocurrency.value
    currency = currency.value
    return requests.get(f"https://bitbay.net/API/Public/{cryptocurrency}{currency}/orderbook.json")


def print_orders(response, operation: Operation, cryptocurrency: Cryptocurrency, currency: Currency, limit: int = 5):
    cryptocurrency = cryptocurrency.value
    currency = currency.value

    print(f"\n\n# {cryptocurrency}/{currency} {operation.name} ORDERS\n")

    result_table = create_table(["No.", cryptocurrency, currency], ["l", "c", "c"], ["i", "t", "f"], ["l", "r", "r"])

    for x, i in zip(response[operation.value], range(1, limit + 1)):
        amount = "{:.8f}".format(x[1])
        price = round(x[0] * x[1], 2)
        result_table.add_row([i, amount, price])

    print(result_table.draw())


def create_table(header, header_align, cols_dtype, cols_align, precision=2, deco=Texttable.HEADER):
    table = Texttable()
    table.header(header)
    table.set_header_align(header_align)
    table.set_cols_dtype(cols_dtype)
    table.set_cols_align(cols_align)
    table.set_precision(precision)
    table.set_deco(deco)
    return table


def task2():
    while True:
        responses = []
        currencies = []
        for c in Cryptocurrency:
            response = make_request(c, Currency.USD)
            if response:
                responses.append(response.json())
                currencies.append([c, Currency.USD])
            else:
                print(f"Error {response.status_code} for {c.value}/USD request!")

        print_differences(responses, currencies)
        time.sleep(5)


def print_differences(responses, currencies):
    differences_table = create_table(["CURRENCIES", "BID", "ASK", "%"], ["l", "c", "c", "c"], ["i", "f", "f", "f"], ["c", "r", "r", "r"])

    for r, c in zip(responses, currencies):
        bid = r["bids"][0][0]
        ask = r["asks"][0][0]
        result = (1 - (ask - bid) / bid) * 100
        differences_table.add_row([f"{c[0].value}/{c[1].value}", bid, ask, result])

    print("\n", differences_table.draw())


if __name__ == '__main__':
    main()
