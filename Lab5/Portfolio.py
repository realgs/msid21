import itertools
import json

from tabulate import tabulate


class Portfolio:
    def __init__(self, apiClasses, configFile, tax):
        self.__apiClasses = apiClasses
        self.__configFile = configFile
        self.__tax = tax
        self.__baseCurrency = None
        self.__resources = None
        self.__apis = None
        self.__arbitrages = None
        self.__saleProfits = None
        self.__percent = None

    def configure(self, configFile=None):
        if not configFile:
            configFile = self.__configFile

        try:
            with open(configFile, "r") as config_file:
                data = json.load(config_file)

            self.__baseCurrency = data['base_currency']
            self.__resources = data['resources']

        except FileNotFoundError:
            print("File '{}' not found.".format(self.__configFile))
        except KeyError as ke:
            print("File error - {} not found. Please reformat file.".format(ke))

        if not self.__baseCurrency or not self.__resources:
            exit()

        resources_signs = list(self.__resources.keys())

        self.__apis = []

        for apiClass in self.__apiClasses:
            self.__apis.append(apiClass(resources_signs))

        percent = 10

        while True:
            try:
                percent = float(input("Percent you want to calculate: "))
                break
            except Exception:
                continue

        self.__percent = percent

    def calculate(self):
        self.__calculateSaleProfits()
        self.__calculateArbitrages()

    def __calculateSaleProfits(self):
        sale_profits = {}
        apis_profits = {}

        for resource_name in self.__resources.keys():
            apis_profits[resource_name] = {}
            sale_profits[resource_name] = [resource_name,
                                           self.__resources[resource_name]['volume'],
                                           0, 0, 0, 0, 0, None]

        for api in self.__apis:
            self.__calculateApiSaleProfits(api, apis_profits)

        for resource_name in self.__resources.keys():
            offers = sorted(list(apis_profits[resource_name].items()), key=lambda x: x[1][1], reverse=True)

            if not offers:
                sale_profits.pop(resource_name)
                continue

            best_offer = offers[0]
            sale_profits[resource_name][1:8] = best_offer[1] + [best_offer[0].sign]

        self.__saleProfits = sorted(list(sale_profits.values()), key=lambda x: x[0])

    def __calculateApiSaleProfits(self, api, apisProfits):
        for resource_name in self.__resources.keys():
            orderbook = api.getOrderbook((resource_name, self.__baseCurrency))

            if not orderbook:
                continue

            bids = orderbook['bids']

            volume_for_sale = self.__resources[resource_name]['volume']
            average_price = self.__resources[resource_name]['price']

            sale = Portfolio.__calculateSale(bids, volume_for_sale, api)

            volume = sale['volume']

            if volume <= 0:
                continue

            price = sale['price']
            offers = sale['offers']

            value = Portfolio.__calculateValue(offers, api, resource_name)

            if value <= 0:
                continue

            api_profits = apisProfits[resource_name][api] = []

            api_profits += [volume, price, value]

            percent_sale = Portfolio.__calculateSale(bids, volume_for_sale, api, percent=self.__percent)
            percent_offers = percent_sale['offers']
            percent_volume = percent_sale['volume']

            percent_value = Portfolio.__calculateValue(percent_offers, api, resource_name)

            api_profits.append(percent_value)

            value_netto = value - (value - volume * average_price) * self.__tax
            percent_value_netto = percent_value - (percent_value - percent_volume * average_price) * self.__tax

            api_profits += [value_netto, percent_value_netto]

    @staticmethod
    def __calculateSale(bids, volumeForSale, api, percent=100):
        volumeForSale = volumeForSale * percent * 0.01
        result = {}
        offers = []
        bids_volume = 0
        price_sum = 0
        value = 0

        for bid in bids:
            if bids_volume + bid[0] >= volumeForSale:
                offers.append((volumeForSale - bids_volume, bid[1]))
                bids_volume = volumeForSale
                price_sum += bid[1]
                break

            bids_volume += bid[0]
            price_sum += bid[1]
            offers.append(bid)

        result['volume'] = bids_volume
        result['price'] = price_sum / len(offers)
        result['offers'] = offers

        return result

    @staticmethod
    def __calculateValue(offers, api, resourceName):
        value = 0
        fees = api.fees

        if fees:
            taker_fee = api.fees['taker']
            transfer_fee = api.fees['transfer'][resourceName]
        else:
            taker_fee = 0
            transfer_fee = 0

        for offer in offers:
            value += offer[0] * offer[1] * (1 - taker_fee)

        value -= transfer_fee

        return value

    def __calculateArbitrages(self):
        self.__arbitrages = set()

        apis_pairs = itertools.permutations(self.__apis, 2)

        for api1, api2 in apis_pairs:
            markets = Portfolio.__findCommonMarkets(api1, api2)

            for market in markets:
                arbitrage = Portfolio.__calculateArbitrage(api1, api2, market)

                if arbitrage[1] > 0:
                    self.__arbitrages.add(arbitrage)

        self.__arbitrages = sorted(self.__arbitrages, key=lambda x: float(x[1]), reverse=True)

    @staticmethod
    def __findCommonMarkets(api1, api2):
        markets1 = api1.markets
        markets2 = api2.markets

        return markets1 & markets2

    @staticmethod
    def __calculateArbitrage(api1, api2, market):
        asks = api1.getOrderbook(market)["asks"]
        bids = api2.getOrderbook(market)["bids"]

        volumes_to_trade = Portfolio.__calculateVolumesToTrade(asks, bids)

        asks = volumes_to_trade["asks"]
        bids = volumes_to_trade["bids"]

        asks_taker_fee = api1.fees["taker"]
        bids_taker_fee = api2.fees["taker"]

        purchase_cost = 0
        purchased_volume = 0

        for (volume, price) in asks:
            purchase_cost += price * volume
            purchased_volume += volume * (1 - asks_taker_fee)

        purchased_volume -= api1.fees["transfer"][market[1]]

        sale_profit = 0

        for (volume, price) in bids:
            if purchased_volume - volume <= 0:
                sale_profit += price * purchased_volume * (1 - bids_taker_fee)
                break

            purchased_volume -= volume
            sale_profit += price * volume * (1 - bids_taker_fee)

        difference = sale_profit - purchase_cost

        return market, difference, (api1, api2)

    @staticmethod
    def __calculateVolumesToTrade(asks, bids):
        result = {"asks": [], "bids": []}

        if not asks or not bids:
            return result

        best_ask = asks[0]
        best_bid = bids[0]

        if best_ask[1] >= best_bid[1]:
            max_volume = min(best_ask[0], best_bid[0])
            result["asks"].append((max_volume, best_ask[1]))
            result["bids"].append((max_volume, best_bid[1]))

            return result

        for i in range(len(asks) - 1, -1, -1):
            ask = asks[i]
            if ask[1] < best_bid[1]:
                bids_temp = []

                for bid in bids:
                    if ask[1] < bid[1]:
                        bids_temp.append(bid)
                    else:
                        break
                bids = bids_temp
                asks = asks[:i + 1]
                break

        bids_volume = 0
        asks_volume = 0

        for bid in bids:
            bids_volume += bid[0]

        for ask in asks:
            asks_volume += ask[0]

        max_volume = min(bids_volume, asks_volume)

        bids_volume = 0
        asks_volume = 0

        for bid in bids:
            if bids_volume + bid[0] >= max_volume:
                result["bids"].append((max_volume - bids_volume, bid[1]))
                break

            bids_volume += bid[0]
            result["bids"].append(bid)

        for ask in asks:
            if asks_volume + ask[0] >= max_volume:
                result["asks"].append((max_volume - asks_volume, ask[1]))
                break

            asks_volume += ask[0]
            result["asks"].append(ask)

        return result

    def __createTable(self):
        table = [["NAZWA", "ILOSC", "CENA", "WARTOSC", "WARTOSC {}%".format(self.__percent), "WARTOSC NETTO",
                  "WARTOSC {}% NETTO".format(self.__percent), "GIELDA", "   ", "ARBITRAZ"]]

        sale_profits_size = len(self.__saleProfits)
        arbitrages_size = len(self.__arbitrages)

        rows_number = max(sale_profits_size, arbitrages_size)

        value_sum = 0
        percent_value_sum = 0
        netto_value_sum = 0
        netto_percent_value_sum = 0

        for i in range(rows_number):
            resource_name = None
            volume = None
            price = None
            value = None
            percent_value = None
            netto_value = None
            netto_percent_value = None
            exchange = None
            arbitrage_market = (None, None)
            arbitrage_difference = None
            arbitrage_api1 = None
            arbitrage_api2 = None
            arbitrage = None

            if i < sale_profits_size:
                resource_name, volume, price, value, percent_value, netto_value, netto_percent_value, exchange \
                    = self.__saleProfits[i]

                value_sum += value
                percent_value_sum += percent_value
                netto_value_sum += netto_value
                netto_percent_value_sum += netto_percent_value

            if i < arbitrages_size:
                arbitrage_market, arbitrage_difference, (arbitrage_api1, arbitrage_api2) = self.__arbitrages[i]
                arbitrage = "{}-{}, {}-{}, +{:.8f}{}".format(arbitrage_api1.sign,
                                                             arbitrage_api2.sign,
                                                             arbitrage_market[0],
                                                             arbitrage_market[1],
                                                             arbitrage_difference,
                                                             arbitrage_market[0])

            if resource_name:
                table.append([resource_name,
                              "{0:.8f}".format(volume),
                              "{0:.2f}".format(price),
                              "{0:.2f}".format(value),
                              "{0:.2f}".format(percent_value),
                              "{0:.2f}".format(netto_value),
                              "{0:.2f}".format(netto_percent_value),
                              exchange,
                              "   ",
                              arbitrage])
            else:
                table.append([resource_name,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              exchange,
                              "   ",
                              arbitrage])

        table.append([" ", " ", " ", " ", " ", " ", " ", " ", " ", " "])

        table.append(["SUMA",
                      None,
                      None,
                      "{0:.2f}".format(value_sum),
                      "{0:.2f}".format(percent_value_sum),
                      "{0:.2f}".format(netto_value_sum),
                      "{0:.2f}".format(netto_percent_value_sum),
                      None,
                      "   ",
                      None])

        return table

    def printTable(self):
        table = self.__createTable()
        print('\n' + tabulate(table, headers='firstrow', tablefmt='fancy_grid',
                              colalign=["center", "right", "right", "right", "right", "right", "right", "center",
                                        "center", "left"]))
        print()
