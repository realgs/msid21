from wallet.logic import transactions_to_wallet
from wallet.markets import wallet_valuation, wallet_partial_valuation

from wallet.tax import tax_estimate

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    # data = yf.download(tickers="BTC-USD", start=datetime.datetime.today().date())
    # print(data)

    # add_transaction("BTC", "USD", 18997, 3.98, datetime.datetime.today())
    # add_transaction("AAPL", "USD", 104, 3, datetime.datetime.today())

    wallet = transactions_to_wallet()
    print(wallet)

    ww = wallet_valuation()
    print(ww)
