import requests


def main():
    task1()
    task2()


def task1():
    print_orders("bids", "BTC", "USD")
    print_orders("asks", "BTC", "USD")
    print_orders("bids", "LTC", "USD")
    print_orders("asks", "LTC", "USD")
    print_orders("bids", "DASH", "USD")
    print_orders("asks", "DASH", "USD")


def print_orders(operation: str, cryptocurrency: str, currency: str, limit: int = 5):
    response = requests.get(f"https://bitbay.net/API/Public/{cryptocurrency}{currency}/orderbook.json").json()

    print(f"\n\n# {cryptocurrency}-{currency} {operation} orders\n")

    for x, i in zip(response[operation], range(1, limit + 1)):
        amount = "{:.8f}".format(x[1])
        price = "{:.2f}".format(round(x[0] * x[1], 2))
        print(f"{i}. {amount} {cryptocurrency} - {price} {currency}")


def task2():
    pass


if __name__ == '__main__':
    main()
