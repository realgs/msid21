from utils import read_json, save_json


class Wallet:
    def __init__(self, filename):
        self.read_from_json(filename)

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

    def add_resource(self, name, quantity, rate, res_type):
        if res_type == 1:
            self.__currency.append({
                'name': name,
                'quantity': quantity,
                'rate': rate
            })
        elif res_type == 2:
            self.__crypto_currency.append({
                'name': name,
                'quantity': quantity,
                'rate': rate
            })
        elif res_type == 3:
            self.__polish_stock.append({
                'name': name,
                'quantity': quantity,
                'rate': rate
            })
        elif res_type == 4:
            self.__foreign_stock.append({
                'name': name,
                'quantity': quantity,
                'rate': rate
            })

    def save_to_json(self):
        resources = {'base_currency': self.__base_currency, 'currency': self.__currency,
                     'crypto_currency': self.__crypto_currency, 'polish_stock': self.__polish_stock,
                     'foreign_stock': self.__foreign_stock}
        save_json(resources)

    def read_from_json(self, filename):
        portfolio_data = read_json(filename)
        self.__base_currency = portfolio_data["base_currency"]
        self.__currency = portfolio_data["currency"]
        self.__crypto_currency = portfolio_data["crypto_currency"]
        self.__polish_stock = portfolio_data["polish_stock"]
        self.__foreign_stock = portfolio_data["foreign_stock"]
