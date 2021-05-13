import random

import pandas as pd

import market_daemon as md
from market_daemon import MarketDaemon
from market_daemon.parsers import *

CONFIG_PATH = "config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")
    bitbay.market_parser = bitbay_request_to_pairs

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.orderbook_parser = bittrex_parser
    bittrex.market_parser = bittrex_request_to_pairs

    aw = md.arbitrage_stream(bitbay, bittrex, "BTC", "EUR")

    # Zad 1 (10 pkt)
    print(bittrex.get_joint_pairs(bitbay))

    # Zad 2
    print(md.check_3_random_pairs(bitbay, bittrex))

    while True:
        next(aw)
