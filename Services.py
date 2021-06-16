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

            if category == 'crypto_currency':
                arbitrage = self.__get_arbitrage(resource_name, resource_quantity)
                arbitrage_str = f'{arbitrage["market"]}, {arbitrage["exchange"]}, {round(arbitrage["value"], 5)}'
            else:
                arbitrage_str = ' - '

            markings.append(
                {'name': resource_name, 'quantity': resource_quantity, 'rate': resource_rate,
                 'price': round(best_price, 2), 'depth_price': round(depth_best_price, 2), 'with_tax': netto,
                 'depth_with_tax': depth_netto, 'exchange': exchange_name_best_price,
                 'arbitrage': arbitrage_str if category == 'crypto_currency' else ' - '})

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

    @staticmethod
    def sell_in_bids(bids, quantity):
        left_volume = quantity
        price = 0
        for bid in bids:
            if left_volume >= bid['quantity']:
                price += bid['quantity'] * bid['rate']
                left_volume -= bid['quantity']
            elif left_volume > 0:
                price += left_volume * bid['rate']
                left_volume = 0

        return price

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

    def __sell_crypto(self, resource, quantity, base):
        value = []
        _, bidsBittrex = API['crypto_currency']['bittrex'].orderbook(resource, 'USD')
        _, bidsBitbay = API['crypto_currency']['bitbay'].orderbook(resource, 'USD')

        r1 = self.sell_in_bids(bidsBittrex, quantity)
        r2 = self.sell_in_bids(bidsBitbay, quantity)

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

    @staticmethod
    def __find_common_pairs(first, second):
        return list(set(first).intersection(second))

    def __get_arbitrage(self, currency_name, currency_quantity):
        arbitrage = []
        common_markets = self.__find_common_pairs(API['crypto_currency']['bitbay'].markets,
                                                  API['crypto_currency']['bittrex'].markets)
        if common_markets:
            available_markets = [market for market in common_markets if market.split('-')[0] in currency_name]

            for market in available_markets:
                arbitrage.append(self.__find_arbitrage_for_market(market, currency_quantity)[0])

            return max(arbitrage, key=lambda x: x['value'])

    def __find_arbitrage_for_market(self, market, resource_quantity):
        arbitrage = []
        own_currency, currency_to_buy = market.split('-')
        btb_asks, btb_bids = API['crypto_currency']['bitbay'].orderbook(own_currency, currency_to_buy)
        btx_asks, btx_bids = API['crypto_currency']['bittrex'].orderbook(own_currency, currency_to_buy)
        arbitrages_btx_bit = self.__all_arbitrages(btb_bids, btx_asks, API['crypto_currency']['bittrex'].taker_fee,
                                                   API['crypto_currency']['bitbay'].taker_fee,
                                                   API['crypto_currency']['bittrex'].transfer_fee(currency_to_buy),
                                                   resource_quantity)
        arbitrages_bit_btx = self.__all_arbitrages(btx_bids, btb_asks, API['crypto_currency']['bitbay'].taker_fee,
                                                   API['crypto_currency']['bittrex'].taker_fee,
                                                   API['crypto_currency']['bitbay'].transfer_fee(currency_to_buy),
                                                   resource_quantity)

        if arbitrages_btx_bit:
            arbitrage.append({'market': market, 'exchange': 'BTX-BIT', 'value': arbitrages_btx_bit[0]})
        if arbitrages_bit_btx:
            arbitrage.append({'market': market, 'exchange': 'BIT-BTX', 'value': arbitrages_bit_btx[0]})

        if arbitrage:
            return sorted(arbitrage, key=lambda i: i['value'], reverse=True)
        else:
            return {'market': '-', 'exchange': '-', 'value': 0}

    @classmethod
    def __all_arbitrages(cls, bid_offers, ask_offers, ask_taker, bid_taker, ask_transfer, resource_quantity):
        possible_arbitrages = []
        for offer in ask_offers:
            invest_rate = offer['rate']
            invest_quantity = offer['quantity']

            if resource_quantity >= invest_quantity:
                bought_volume = cls.get_price_sell(invest_quantity, invest_rate, ask_taker) - ask_transfer
                earn = cls.__get_best_sell_price(bid_offers, bid_taker, bought_volume)
                possible_arbitrages.append(earn - invest_quantity)

        possible_arbitrages.sort()
        return possible_arbitrages

    @classmethod
    def __get_best_sell_price(cls, bid_offers, bid_taker, volume_to_sell):
        earn = 0
        num_of_offer = 0
        while volume_to_sell > 0 and num_of_offer < len(bid_offers):
            volume_to_buy = bid_offers[num_of_offer]['quantity']
            rate = bid_offers[num_of_offer]['rate']
            sell_price = cls.get_price_buy(volume_to_buy, rate, bid_taker)

            if volume_to_sell >= sell_price > 0:
                earn += volume_to_buy
                volume_to_sell -= sell_price

            num_of_offer += 1
        return earn
