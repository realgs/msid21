from BitBayApi import BitBayApi
from BittrexApi import BittrexApi
from Portfolio import Portfolio

CONFIG_FILE = "config.json"
API_CLASSES = {BitBayApi, BittrexApi}
TAX = 0.19


def main():
    portfolio = Portfolio(API_CLASSES, CONFIG_FILE, TAX)
    portfolio.configure()
    portfolio.calculate()
    portfolio.printTable()


if __name__ == '__main__':
    main()
