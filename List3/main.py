import market_daemon as md
from market_daemon.parsers import bittrex_parser

CONFIG_PATH = "config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.set_parser(bittrex_parser)

    bitbay.get_orders("BTC", size=3)

    # Zad 1 a-b (5 pkt)
    buy = md.compare_stream(bitbay, bittrex, "XLM")
    sell = md.compare_stream(bitbay, bittrex, "ETH", kind="sell")

    # Zad 1 c
    ss = md.compare_transfer_stream(bitbay, bittrex, "BTC")

    # Zad 2 (5 pkt)
    aw = md.arbitrage_stream(bittrex, bitbay, "ETH")

    while True:
        next(aw)
