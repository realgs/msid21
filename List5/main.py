import datetime

import pandas as pd

import market_daemon as md
from market_daemon import optimizers
from market_daemon.parsers import *

from wallet.markets import wallet_valuation

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

    x = bitbay.valuation("BTC", 2, base="USD")
    print(x)

    # add_instrument("AAPL", "USD", 993.232, 4, datetime.datetime.today())
    # add_instrument("TSLA", "USD", 609, 2, datetime.datetime.today())

    df = wallet_valuation("PLN")
    print(df)
