from utils import read_json


class Wallet:
    def __init__(self, filename):
        portfolio_data = read_json(filename)
        self.__base_currency = portfolio_data["base_currency"]
        self.__currency = portfolio_data["currency"]
        self.__crypto_currency = portfolio_data["crypto_currency"]
        self.__polish_stock = portfolio_data["polish_stock"]
        self.__foreign_stock = portfolio_data["foreign_stock"]

    @property
    def base_currency(self):
        return self.__base_currency

    @property
    def currency(self):
        return self.__currency

    @property
    def crypto_currencies(self):
        return self.__crypto_currency

    @property
    def polish_stock(self):
        return self.__polish_stock

    @property
    def foreign_stock(self):
        return self.__foreign_stock
