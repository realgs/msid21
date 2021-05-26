from API.Bitbay import Bitbay
from API.Bittrex import Bittrex
from API.Yahoo import Yahoo
from Wallet import Wallet

API = {
    "currency": None,
    "crypto_currency": {
        "bitbay": Bitbay(),
        "bittrex": Bittrex()
    },
    "polish_stock": None,
    "foreign_stock": Yahoo()
}


class Service:

    @classmethod
    def get_markings(cls, wallet: Wallet):
        markings = []
        for crypto in wallet.crypto_currencies:
            markings.append({"name": crypto['name'],
                             "price": cls.__sell_crypto(crypto['name'], crypto['quantity'],
                                                        wallet.base_currency)})
        for stock in wallet.foreign_stock:
            markings.append({"name": stock['name'],
                             "price": cls.__sell_foreign_stock(stock['name'], stock['quantity'],
                                                               wallet.base_currency)})

        return markings

    @classmethod
    def __sell_crypto(cls, resource, quantity, base):
        # TODO add multiprocessing
        value = []
        for key in API['crypto_currency']:
            _, bids = API['crypto_currency'][key].orderbook(resource, base)

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
            value.append(price)
        return max(value)

    @classmethod
    def __sell_polish_stock(cls, resource, quantity, base):
        return None

    @classmethod
    def __sell_foreign_stock(cls, resource, quantity, base):
        return quantity * API['foreign_stock'].get_price(resource, base)
