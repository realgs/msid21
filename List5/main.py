from wallet.logic import read_wallet

from wallet.tax import tax_estimate

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    # data = yf.download(tickers="BTC-USD", start=datetime.datetime.today().date())
    # print(data)

    # add_transaction("BTC", "USD", 18997, 3.98, datetime.datetime.today())
    # add_transaction("AAPL", "USD", 104, 3, datetime.datetime.today())

    wallet = read_wallet()
    print(wallet)

    tax = tax_estimate("BTC", 1.2, 18999)
    print(tax)
