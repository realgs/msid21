import datetime

import market_daemon as md
from market_daemon import optimizers
from market_daemon.parsers import *
from wallet.logic import add_transaction, read_transactions, read_wallet, update_wallet

from wallet.markets import wallet_valuation, wallet_partial_valuation
from wallet.tax import tax_estimate, taxable_transactions

CONFIG_PATH = "api_config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")
    bitbay.market_parser = bitbay_request_to_pairs

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.orderbook_parser = bittrex_parser
    bittrex.market_parser = bittrex_request_to_pairs

    ss = md.arbitrage_stream(bitbay, bittrex, "EOS", "USDT", solver=optimizers.LinprogArbitrage())
    # print(next(ss))

    # Zad 1 (10 pkt)
    # print(bittrex.get_joint_pairs(bitbay))

    # Zad 2 (2 pkt)
    # print(md.check_3_random_pairs(bitbay, bittrex))

    # Zad 3 (8 pkt)
    # df = md.arbitrage_summary(bittrex, bitbay, solver=optimizers.LinprogArbitrage())
    # print(df[["pair", "profit", "profitability"]].head(10))

    # data = yf.download(tickers="BTC-USD", start=datetime.datetime.today().date())
    # print(data)

    # add_transaction("KGH.WSE", "PLN", 187, -0.755, datetime.datetime.today())
    # add_transaction("CDR.WSE", "PLN", 54454, 16.45, datetime.datetime.today())

    # add_transaction("BTC", "USD", 18997, 3.98, datetime.datetime.today())
    # add_transaction("AAPL", "USD", 104, 3, datetime.datetime.today())

    wallet = read_wallet()
    print(wallet)

    update_wallet()

    # res = taxable_transactions(df, "KGH.WSE", kind="sell")
    # print(res)

    # tax_estimate(df, "AAPL")
