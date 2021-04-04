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
    # PLN = "PLN"


def main():
    # task1()
    task2()


def task1():
    for c in Cryptocurrency:
        response = make_request(c, Currency.USD)
        if response:
            print_orders(response.json(), Operation.BUY, c, Currency.USD)
            print_orders(response.json(), Operation.SELL, c, Currency.USD)
        else:
            print(f"Error {response.status_code} for {c}/USD request!")


def make_request(cryptocurrency: Cryptocurrency, currency: Currency):
    cryptocurrency = cryptocurrency.value
    currency = currency.value
    return requests.get(f"https://bitbay.net/API/Public/{cryptocurrency}{currency}/orderbook.json")


def print_orders(response, operation: Operation, cryptocurrency: Cryptocurrency, currency: Currency, limit: int = 5):
    cryptocurrency = cryptocurrency.value
    currency = currency.value

    print(f"\n\n# {cryptocurrency}/{currency} {operation.name} ORDERS\n")

    result_table = create_table(cryptocurrency, currency)

    for x, i in zip(response[operation.value], range(1, limit + 1)):
        amount = "{:.8f}".format(x[1])
        price = round(x[0] * x[1], 2)
        result_table.add_row([i, amount, price])

    print(result_table.draw())


def create_table(cryptocurrency, currency):
    table = Texttable()
    table.header(["No.", cryptocurrency, currency])
    table.set_cols_dtype(["i", "t", "f"])
    table.set_cols_align(["l", "r", "r"])
    table.set_precision(2)
    table.set_deco(Texttable.HEADER)
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
                print(f"Error {response.status_code} for {c}/USD request!")

        print_differences(responses, currencies)
        time.sleep(5)


def print_differences(responses, currencies):
    table = Texttable()
    table.header(["CURRENCIES", "BID", "ASK", "%"])
    table.set_cols_dtype(["t", "f", "f", "f"])
    table.set_cols_align(["l", "r", "r", "r"])
    table.set_precision(2)
    table.set_deco(Texttable.HEADER)

    for r, c in zip(responses, currencies):
        bid = r["bids"][0][0]
        ask = r["asks"][0][0]
        result = (1 - (ask - bid) / bid) * 100
        table.add_row([f"{c[0].value}/{c[1].value}", bid, ask, result])

    print()
    print(table.draw())


if __name__ == '__main__':
    main()
