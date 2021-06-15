from BitBayApi import BitBayApi
from BittrexApi import BittrexApi
from Portfolio import Portfolio

CONFIG_FILE = "config.json"
API_CLASSES = {BitBayApi, BittrexApi}


def main():
    portfolio = Portfolio(API_CLASSES, CONFIG_FILE)
    portfolio.configure()
    portfolio.calculate()
    portfolio.printTable()


if __name__ == '__main__':
    main()
