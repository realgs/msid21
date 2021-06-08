import json

import cryptos
from apis import yahoo
from apis import stooq
from apis import nbp

WALLET_FILE = "configs/wallet.json"
VAT = 0.19
BASE = 'USD'


def read_wallet():
    with open(WALLET_FILE) as f:
        return json.load(f)


def appraise(percent):
    wallet = read_wallet()
    for resource in wallet:
        if resource['type'] != 'crypto':
            rate = 0
            if resource['type'] == 'us_stock':
                rate = yahoo.get_rate(resource['symbol'])

            elif resource['type'] == 'pl_stock':
                pln_rate = stooq.get_rate(resource['symbol'])
                nbp_rate = nbp.get_rate(BASE, resource['base'])
                rate = pln_rate / nbp_rate
                resource['price'] /= nbp_rate
                resource['base'] = BASE

            elif resource['type'] == 'currency':
                rate = nbp.get_rate(resource['symbol'], resource['base'])

            resource['sell_rate'] = rate
            resource['sell_value'] = rate * resource['quantity'] * percent
            sell_profit = resource['sell_value'] - (resource['price'] * resource['quantity'] * percent)
            resource['sell_profit'] = sell_profit * (1 - VAT) if sell_profit > 0 else sell_profit
            resource['market'] = ''

            if resource['type'] == 'currency':
                nbp_rate = nbp.get_rate(BASE, resource['base'])
                resource['sell_value'] /= nbp_rate
                resource['sell_profit'] /= nbp_rate
                resource['base'] = BASE

        else:
            appraisal = cryptos.appraise(resource['quantity'] * percent, resource['symbol'] + BASE)
            best_price = appraisal[0]
            for a in appraisal:
                if a[1] > best_price[1]:
                    best_price = a

            resource['sell_rate'] = best_price[2]
            resource['sell_value'] = best_price[1]
            sell_profit = best_price[1] - (resource['price'] * resource['quantity'] * percent)
            resource['sell_profit'] = sell_profit * (1 - VAT) if sell_profit > 0 else sell_profit
            resource['market'] = best_price[0]

    return wallet
