import json
import constants


class Wallet:
    def __init__(self):
        self.resources = self.read()

    def read(self):
        try:
            with open('config.json') as config:
                wallet = json.load(config)
                config.close()
            return wallet
        except:
            default = {
                constants.BASE_CURRENCY: 'USD',
                constants.STOCKS: {},
                constants.CURRENCIES: {},
                constants.CRYPTOCURRENCIES: {}
            }
            return default

    def save(self):
        json_wallet = json.dumps(self.resources, indent=4)
        with open('config.json', 'w') as outfile:
            outfile.write(json_wallet)

    def add(self, type, resource, quantity, price):
        self.resources[type][resource] = {}
        self.resources[type][resource][constants.QUANTITY] = quantity
        self.resources[type][resource][constants.PRICE] = price
        self.save()
