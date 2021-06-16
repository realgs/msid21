import yfinance
import marketApi
import consts
import currencyMarket

class ForeignStockMarket(marketApi.Market):
    def __init__(self, name):
        super().__init__(name, consts.FS["type"])
        self.__currencyMarket = currencyMarket.CurrencyMarket("foreign stock market")

    def getSellPrice(self, symbol, volume, percentage):
        ticker = yfinance.Ticker(symbol)
        try:
            return round(self.__averagePrice(ticker) * volume * percentage / 100, 2)
        except KeyError:
            return -1
        
    def __averagePrice(self, ticker):
        return self.__currencyMarket.getSellPrice("USD", 1, 100) * (ticker.info['dayLow'] + ticker.info['dayHigh'] / 2.0)
        