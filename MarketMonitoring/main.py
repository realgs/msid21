import pandas as pd

from wallet.logic import read_wallet
from wallet.markets import wallet_valuation, wallet_partial_valuation, wallet_arbitrage_summary

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    print("Zad 1")
    wallet = read_wallet()
    print(wallet)

    print("Zad 2")
    ww = wallet_valuation()
    print(ww)
    print(ww.sum()[["valuationEur", "netValuationEur"]])

    print("Zad 3")
    wpw = wallet_partial_valuation(fraction=0.01)
    print(wpw)
    print(wpw.sum()[["valuationEur", "netValuationEur"]])

    # Zad 4, 5 - uwzględniono powyżej

    print("Zad 6")
    arbitrage = wallet_arbitrage_summary()
    print(arbitrage)

    # Zad 7 - MainWindow.py
