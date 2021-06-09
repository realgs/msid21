import json

import cryptos
from apis import yahoo
from apis import stooq
from apis import nbp

WALLET_FILE = "configs/wallet.json"
VAT = 0.19
BASE = 'USD'


# Read wallet from file
def read_wallet():
    with open(WALLET_FILE) as f:
        return json.load(f)


# Appraise wallet
def appraise(percent):
    wallet = read_wallet()
    for resource in wallet:
        if resource['type'] != 'crypto':
            rate = 0

            # Get rates for US Stocks
            if resource['type'] == 'us_stock':
                if resource['base'] != BASE:
                    nbp_rate = nbp.get_rate(BASE, resource['base'])
                    resource['base'] = BASE
                    resource['price'] /= nbp_rate
                rate = yahoo.get_rate(resource['symbol'])

            # Get rates for PL Stocks
            elif resource['type'] == 'pl_stock':
                pln_rate = stooq.get_rate(resource['symbol'])
                nbp_rate = nbp.get_rate(BASE, resource['base'])
                rate = pln_rate / nbp_rate
                resource['price'] /= nbp_rate
                resource['base'] = BASE

            # Get rates for currencies
            elif resource['type'] == 'currency':
                rate = nbp.get_rate(resource['symbol'], resource['base'])

            # Appraise resources
            resource['sell_rate'] = rate
            resource['sell_value'] = rate * resource['quantity'] * percent
            sell_profit = resource['sell_value'] - (resource['price'] * resource['quantity'] * percent)
            resource['sell_profit'] = sell_profit * (1 - VAT) if sell_profit > 0 else sell_profit
            resource['market'] = ''

            # Convert currencies values to BASE currency
            if resource['type'] == 'currency':
                nbp_rate = nbp.get_rate(BASE, resource['base'])
                resource['sell_value'] /= nbp_rate
                resource['sell_profit'] /= nbp_rate
                resource['base'] = BASE

        # Get rates and do deep appraise for cryptos
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
            arbitrage = cryptos.arbitrage_for_pair(resource['symbol'] + resource['base'])
            resource['arbitrage'] = f'{arbitrage[0][0]} {arbitrage[0][6]} {round(arbitrage[0][5], 2)}%\n{arbitrage[0][1]}-{arbitrage[0][3]}\n\n' \
                                    f'{arbitrage[1][0]} {arbitrage[1][6]} {round(arbitrage[1][5], 2)}%\n{arbitrage[1][1]}-{arbitrage[1][3]}'

    return wallet
