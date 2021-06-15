import API_OPERATIONS
import BITBAY
import BITTREX
import Wallet


def main():

    bitbay = BITBAY.Bitbay()
    bittrex = BITTREX.Bittrex()
    Wallet.sell_currency("BTC", 50, bitbay)
    """
    arbitrage_book = API_OPERATIONS.arbitrage_book(bittrex, 0, bitbay, 0)
    for item in arbitrage_book:
        print(f'market: {item[0]} possible money earn: {item[1]}')
    data = API_OPERATIONS.sell_currency(1.32, "BTC", 0, "EUR", bitbay)
    print(f"{data[0]} - {data[1]} - {data[2]}")
    """


if __name__ == "__main__":
    main()
