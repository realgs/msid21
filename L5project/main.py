import API_operations
import Bitbay
import Bittrex
import Wallet
import Alpha_vantage
import Raport
import Eod

# Ten main jest tylko do testów, wszystko jest zawarte w gui

def main():
    eod = Eod.Eodhistoricaldata()
    print(eod.request_market_data())


if __name__ == "__main__":
    main()
