import market_daemon as md
from market_daemon.parsers import bittrex_parser

CONFIG_PATH = "config.json"

if __name__ == "__main__":
    bitbay = md.MarketDaemon.build_from_config("bitbay")

    bittrex = md.MarketDaemon.build_from_config("bittrex", CONFIG_PATH)
    bittrex.set_parser(bittrex_parser)

    bitbay.get_orders("BTC")
    bitbay.get_orders("BTCx")

    s = md.compare_stream(bitbay, bittrex, "BTC")
    ss = md.compare_transfer_stream(bitbay, bittrex, "BTC")

    sss = bitbay.stream("BTC")
    for _ in range(5):
        next(sss)

    while True:
        next(s)
        # next(ss)
