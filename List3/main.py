import market_daemon as md
from market_daemon.parsers import bittrex_parser

CONFIG_PATH = "config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.set_parser(bittrex_parser)

    bitbay.get_orders("BTC")
    bitbay.get_orders("BTCx")

    s = md.compare_stream(bitbay, bittrex, "BTC", kind="buy", verbose=True)
    ss = md.compare_transfer_stream(bittrex, bitbay, "ETH")

    while True:
        next(s)
