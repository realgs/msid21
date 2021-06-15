import API_OPERATIONS
import BITBAY
import BITTREX
import Wallet


def main():
    """
    bitbay = BITBAY.Bitbay()
    bittrex = BITTREX.Bittrex()
    Wallet.sell_currency("BTC", 50, bitbay)
    """
    Wallet.update_all()

if __name__ == "__main__":
    main()
