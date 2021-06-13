from multiprocessing import Pool, cpu_count

from API.Bitbay import Bitbay
from API.Bittrex import Bittrex
from API.EOD import EOD
from API.NBP import NBP
from API.Yahoo import Yahoo
from Wallet import Wallet

API = {
    "currency": NBP(),
    "crypto_currency": {
        "bitbay": Bitbay(),
        "bittrex": Bittrex()
    },
    "polish_stock": EOD(),
    "foreign_stock": Yahoo()
}


def search_bids(bids, quantity):
    volume = quantity
    price = 0
    for bid in bids:
        if volume >= bid['quantity']:
            price += bid['quantity'] * bid['rate']
            volume -= bid['quantity']
        elif volume > 0:
            price += volume * bid['rate']
            volume = 0
    if volume == 0:
        pass
    return price


class Service:
    def __init__(self, wallet: Wallet):
        self.__wallet = wallet

    @property
    def base_currency(self):
        return self.__wallet.base_currency

    def analyse_portfolio(self, depth):
        with Pool(processes=cpu_count()) as pool:
            r1 = pool.apply_async(self.analyse_resources_category, ('currency', self.__wallet.currency, depth))
            r2 = pool.apply_async(self.analyse_resources_category,
                                  ('crypto_currency', self.__wallet.crypto_currencies, depth))
            r3 = pool.apply_async(self.analyse_resources_category,
                                  ('polish_stock', self.__wallet.polish_stock, depth))
            r4 = pool.apply_async(self.analyse_resources_category,
                                  ('foreign_stock', self.__wallet.foreign_stock, depth))

            markings = r1.get() + r2.get() + r3.get() + r4.get()

        return markings

    def analyse_resources_category(self, category, resources, depth):
        markings = []
        for resource in resources:
            resource_name = resource['name']
            resource_quantity = float(resource['quantity'])
            resource_rate = float(resource['rate'])

            best_price, exchange_name_best_price = self.__sell_resource(category, resource_name, resource_quantity,
                                                                        self.__wallet.base_currency)
            depth_best_price, _ = self.__sell_resource(category, resource_name, resource_quantity * depth / 100,
                                                       self.__wallet.base_currency)
            netto = self.tax(best_price, resource_quantity, resource_rate, 100)
            depth_netto = self.tax(depth_best_price, resource_quantity, resource_rate, depth)

            markings.append(
                {'name': resource_name, 'quantity': resource_quantity, 'rate': resource_rate,
                 'price': best_price, 'depth_price': round(depth_best_price, 2), 'with_tax': netto,
                 'depth_with_tax': depth_netto, 'exchange': exchange_name_best_price})

        return markings

    def add_resource(self, request):
        name = str(request.form['name'])
        quantity = float(request.form['quantity'])
        rate = float(request.form['rate'])
        if quantity < 0 or rate < 0:
            raise ValueError
        invest_type = int(request.form['type'])
        self.__wallet.add_resource(name, quantity, rate, invest_type)

    def save_to_json(self):
        self.__wallet.save_to_json()

    def read_json(self, filename):
        self.__wallet.read_from_json(filename)

    @staticmethod
    def tax(sell_price, quantity, rate, depth):
        revenue = round(sell_price - (quantity * (depth / 100) * rate), 2)
        return revenue if revenue < 0 else round(revenue * 0.81, 2)

    def __sell_resource(self, resource_category, cur_from, quantity, cur_to):
        if resource_category == 'currency':
            return self.__sell_currency(cur_from, quantity, cur_to)
        elif resource_category == 'crypto_currency':
            return self.__sell_crypto(cur_from, quantity, cur_to)
        elif resource_category == 'polish_stock':
            return self.__sell_polish_stock(cur_from, quantity, cur_to)
        elif resource_category == 'foreign_stock':
            return self.__sell_foreign_stock(cur_from, quantity, cur_to)

    @staticmethod
    def __sell_currency(cur_from, quantity, cur_to):
        return API['currency'].convert(cur_from, quantity, cur_to), ' - '

    @staticmethod
    def __sell_crypto(resource, quantity, base):
        value = []
        _, bidsBittrex = API['crypto_currency']['bittrex'].orderbook(resource, 'USD')
        _, bidsBitbay = API['crypto_currency']['bitbay'].orderbook(resource, 'USD')

        r1 = search_bids(bidsBittrex, quantity)
        r2 = search_bids(bidsBitbay, quantity)

        value.append((API['currency'].convert('USD', r1, base), 'BTX'))
        value.append((API['currency'].convert('USD', r2, base), 'BTB'))

        return max(value, key=lambda item: item[0])

    @staticmethod
    def __sell_polish_stock(resource, quantity, base):
        return quantity * API['polish_stock'].get_price(resource, base), ' - '

    @staticmethod
    def __sell_foreign_stock(resource, quantity, base):
        return quantity * API['foreign_stock'].get_price(resource, base), ' - '

    @staticmethod
    def get_price_buy(volume, rate, taker_fee):
        return volume * (1 + (volume * taker_fee)) * rate

    @staticmethod
    def get_price_sell(volume, rate, taker_fee):
        return volume * (1 - volume * taker_fee) * rate
