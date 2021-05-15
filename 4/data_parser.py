from utils import *
import re
bittrex = "https://api.bittrex.com/api/v1.1/public"
poloniex = "https://poloniex.com/public"

class DataParser:
    @staticmethod
    def common_markets():
        bittrex_markets = DataParser.bittrex_markets()
        poloniex_markets = DataParser.poloniex_markets()
        common_base = bittrex_markets.keys() & poloniex_markets.keys()

        return {key: set(bittrex_markets[key]) & set(poloniex_markets[key]) for key in common_base}


    @staticmethod
    def bittrex_markets():
        response = connect("{}/getmarkets".format(bittrex))
        trading_markets = {}

        for market in response['result']:
            base = market['BaseCurrency']

            if trading_markets.get(base) is None:
                trading_markets[base] = []

            trading_markets[base].append(market['MarketCurrency'])

        return trading_markets

    @staticmethod
    def poloniex_markets():
        response = connect("{}?command=returnOrderBook&currencyPair=all&depth=1".format(poloniex))
        trading_markets = {}

        for currencyPair in response:
            splitted = re.split("_", currencyPair)

            if trading_markets.get(splitted[0]) is None:
                trading_markets[splitted[0]] = []

            trading_markets[splitted[0]].append(splitted[1])

        return trading_markets
