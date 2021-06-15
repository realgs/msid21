import market_daemon
from wallet.logic import transactions_to_wallet, read_wallet
from wallet.markets import wallet_valuation, wallet_partial_valuation, wallet_arbitrage_summary

from wallet.tax import tax_estimate
from wallet.valuation import get_price, get_stooq_price

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    # data = yf.download(tickers="BTC-USD", start=datetime.datetime.today().date())
    # print(data)

    # add_transaction("BTC", "USD", 18997, 3.98, datetime.datetime.today())
    # add_transaction("AAPL", "USD", 104, 3, datetime.datetime.today())

    # wallet = transactions_to_wallet()
    # print(wallet)

    # ww = wallet_partial_valuation(0.2)
    # print(ww)

    # bitbay = market_daemon.MarketDaemon.build_from_config("bitbay")
     #bittrex = market_daemon.MarketDaemon.build_from_config("bittrex")

    wallet = read_wallet()
    print(wallet)

    res = wallet_arbitrage_summary()
    print(res)
