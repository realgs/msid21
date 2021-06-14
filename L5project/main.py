import API_OPERATIONS
import BITBAY
import BITTREX


def main():
    bitbay = BITBAY.Bitbay()
    bittrex = BITTREX.Bittrex()
    arbitrage_book = API_OPERATIONS.arbitrage_book(bittrex, 0, bitbay, 0)
    for item in arbitrage_book:
        print(f'market: {item[0]} possible money earn: {item[1]}')


if __name__ == "__main__":
    main()
