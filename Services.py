from multiprocessing import Pool

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

    @classmethod
    def get_markings(cls, wallet: Wallet):
        markings = []
        for currency in wallet.currency:
            currency['price'] = round(
                cls.__sell_currency(currency['name'], float(currency['quantity']), wallet.base_currency), 2)
            markings.append(currency)
        for crypto in wallet.crypto_currencies:
            crypto['price'] = round(cls.__sell_crypto(crypto['name'], float(crypto['quantity']), wallet.base_currency),
                                    2)
            markings.append(crypto)
        for stock in wallet.polish_stock:
            stock['price'] = round(
                cls.__sell_polish_stock(stock['name'], float(stock['quantity']), wallet.base_currency), 2)
            markings.append(stock)
        for stock in wallet.foreign_stock:
            stock['price'] = round(
                cls.__sell_foreign_stock(stock['name'], float(stock['quantity']), wallet.base_currency), 2)
            markings.append(stock)

        return markings

    @staticmethod
    def __sell_currency(cur_from, quantity, cur_to):
        return API['currency'].convert(cur_from, quantity, cur_to)

    @staticmethod
    def __sell_crypto(resource, quantity, base):
        value = []
        _, bidsBittrex = API['crypto_currency']['bittrex'].orderbook(resource, base)
        _, bidsBitbay = API['crypto_currency']['bitbay'].orderbook(resource, base)

        with Pool(processes=4) as pool:
            r1 = pool.apply_async(search_bids, (bidsBittrex, quantity))
            r2 = pool.apply_async(search_bids, (bidsBitbay, quantity))

            value.append(r1.get())
            value.append(r2.get())

        return max(value)

    @staticmethod
    def __sell_polish_stock(resource, quantity, base):
        return quantity * API['polish_stock'].get_price(resource, base)

    @staticmethod
    def __sell_foreign_stock(resource, quantity, base):
        return quantity * API['foreign_stock'].get_price(resource, base)
