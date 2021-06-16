from wallet.logic import transactions_to_wallet, read_wallet
from wallet.markets import wallet_valuation, wallet_partial_valuation, wallet_arbitrage_summary

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    # Zad 1 - config.json

    print("Zad 2")
    ww = wallet_valuation()
    print(ww)

    print("Zad 3")
    wpw = wallet_partial_valuation(fraction=0.1)
    print(wpw)

    print("Zad 3")
    wpw = wallet_partial_valuation(fraction=0.1)
    print(wpw)

    # Zad 4, 5 - uwzględniono powyżej

    print("Zad 6")
    arbitrage = wallet_arbitrage_summary()
    print(arbitrage)

    wallet = read_wallet()
    print(wallet)

    # Zad 7 - MainWindow.py
