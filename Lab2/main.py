import requests
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
    task1()
    task2()


def task1():
    for c in Cryptocurrency:
        print_orders(Operation.BUY, c, Currency.USD)
        print_orders(Operation.SELL, c, Currency.USD)


def print_orders(operation: Operation, cryptocurrency: Cryptocurrency, currency: Currency, limit: int = 5):
    cryptocurrency = cryptocurrency.value
    currency = currency.value
    response = requests.get(f"https://bitbay.net/API/Public/{cryptocurrency}{currency}/orderbook.json").json()

    print(f"\n\n# {cryptocurrency}-{currency} {operation.name} ORDERS\n")

    result_table = Texttable()
    result_table.header(["No.", cryptocurrency, currency])
    result_table.set_cols_dtype(["i", "t", "f"])
    result_table.set_cols_align(["l", "r", "r"])
    result_table.set_precision(2)
    result_table.set_deco(Texttable.HEADER)

    for x, i in zip(response[operation.value], range(1, limit + 1)):
        amount = "{:.8f}".format(x[1])
        price = round(x[0] * x[1], 2)
        result_table.add_row([i, amount, price])

    print(result_table.draw())


def task2():
    pass


if __name__ == '__main__':
    main()
