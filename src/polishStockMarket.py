import marketApi
import consts
import requests
import currencyMarket
from bs4 import BeautifulSoup

class PolishStockMarket(marketApi.Market):
    def __init__(self, name, url):
        super().__init__(name, consts.PS["type"])
        self.__url = url
        self.__currencyMarket = currencyMarket.CurrencyMarket("polish stock market")

    def getSellPrice(self, symbol, volume, percentage):
        response = self.__getResponse(symbol)
        if response == None:
            return -1 #TODO -1 zmienic na BAD_VALUE czy cos takiego

        return round(self.__getPrice(symbol, response) * volume * percentage / 100, 2)

    def __getResponse(self, symbol):
        try:
            return requests.get(self.__url.format(symbol))
        except requests.exceptions.ConnectionError:
            return None

    def __getPrice(self, symbol, response):
        # print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        op = soup.find(text="Kurs")
        if op == None:
            return -1

        op = op.parent.find("span")
        return self.__currencyMarket.getSellPrice("PLN", 1, 100) * float(op.text)