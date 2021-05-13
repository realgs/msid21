import market_daemon as md
from market_daemon.parsers import *

CONFIG_PATH = "config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")
    bitbay.market_parser = bitbay_request_to_pairs

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.orderbook_parser = bittrex_parser
    bittrex.market_parser = bittrex_request_to_pairs

    print(bittrex.get_joint_pairs(bitbay))

    bitbay.get_orders("BTC", size=3)

    # Zad 1 a-b (5 pkt)
    buy = md.compare_stream(bitbay, bittrex, "XLM")
    sell = md.compare_stream(bitbay, bittrex, "ETH", kind="sell")

    # Zad 1 c
    cs = md.compare_stream(bitbay, bittrex, "BTC", kind="transfer")

    # Zad 2 (5 pkt)
    aw = md.arbitrage_stream(bitbay, bittrex, "BTC", "EUR")

    while True:
        next(aw)
