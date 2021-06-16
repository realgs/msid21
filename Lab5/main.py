import time

from AlphaVantageApi import AlphaVantageApi
from BitBayApi import BitBayApi
from BittrexApi import BittrexApi
from Portfolio import Portfolio

CONFIG_FILE = "config.json"
API_CLASSES = {BitBayApi, BittrexApi, AlphaVantageApi}
TAX = 0.19
DELAY = 15


def main():
    portfolio = Portfolio(API_CLASSES, CONFIG_FILE, TAX)
    portfolio.configure()
    while True:
        portfolio.calculate()
        portfolio.printTable()

        time.sleep(DELAY)


if __name__ == '__main__':
    main()
