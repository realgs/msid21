import requests

from APIs.API import API


class BitBayAPI(API):
    BASEURL = 'https://api.bitbay.net/rest/trading/'
    VALID_CRYPTO_CURR = {'DOT', 'UNI', 'BSV', 'XRP', 'AAVE', 'XTZ', 'LTC', 'UNI', 'LINK', 'DOT', 'BSV', 'XTZ', 'GRT',
                         'AAVE', 'AAVE', 'PAY', 'ETH', 'ZRX', 'BSV', 'ZRX', 'TRX', 'BSV', 'XLM', 'OMG', 'BTC', 'BAT',
                         'LUNA', 'GRT', 'XLM', 'DAI', 'TRX', 'XRP', 'DAI', 'GAME', 'TRX', 'USDC', 'LTC', 'OMG', 'BTC',
                         'OMG', 'COMP', 'LSK', 'EOS', 'MANA', 'MKR', 'DOT', 'XRP', 'BSV', 'COMP', 'LTC', 'LSK', 'XLM',
                         'XRP', 'ETH', 'NPXS', 'UNI', 'TRX', 'ETH', 'BAT', 'LINK', 'TRX', 'GRT', 'XRP', 'XLM', 'EOS',
                         'LTC', 'ETH', 'BTC', 'SRN', 'XLM', 'LUNA', 'LINK'}
    VALID_BASE_CURR = {'BTC', 'ETH', 'USDT', 'BTC', 'USD', 'BTC', 'BTC', 'EUR', 'BTC', 'USDT', 'BTC', 'BTC', 'ETH',
                       'EUR', 'USDT', 'USD', 'USD', 'BTC', 'BTC', 'BTC', 'BTC', 'EUR', 'BTC', 'ETH', 'USDT', 'BTC',
                       'EUR', 'USD', 'BTC', 'USDT', 'ETH', 'BTC', 'USDT', 'USDT', 'BTC', 'USDT', 'USDT', 'USDT', 'USDT',
                       'BTC', 'USD', 'ETH', 'USDT', 'USDT', 'BTC', 'BTC', 'EUR', 'ETH', 'USD', 'USDT', 'BTC', 'BTC',
                       'USDT', 'EUR', 'EUR', 'USD', 'USDT', 'USDT', 'USD', 'EUR', 'EUR', 'EUR', 'BTC', 'BTC', 'BTC',
                       'BTC', 'ETH', 'USD', 'USD', 'USD', 'USDT', 'BTC'}
    VALID_TYPE = {"buy", "sell", "both"}
    TAKER_FEE = 0.0043  # percentage
    TRANSFER_FEE = {
        "AAVE": 0.54, "ALG": 426.0, "AMLT": 1743.0, "BAT": 156.0, "BCC": 0.001, "BCP": 1237.0, "BOB": 11645.0,
        "BSV": 0.003, "BTC": 0.0005, "BTG": 0.001, "COMP": 0.1, "DAI": 81.0, "DASH": 0.001, "DOT": 0.1, "EOS": 0.1,
        "ETH": 0.006, "EXY": 520.0, "GAME": 479.0, "GGC": 112.0, "GNT": 403.0, "GRT": 84.0, "LINK": 2.7, "LML": 1500.0,
        "LSK": 0.3, "LTC": 0.001, "LUNA": 0.02, "MANA": 100.0, "MKR": 0.025, "NEU": 572.0, "NPXS": 46451.0, "OMG": 14.0,
        "PAY": 1523.0, "QARK": 1019.0, "REP": 3.2, "SRN": 5717.0, "SUSHI": 8.8, "TRX": 1.0, "UNI": 2.5, "USDC": 125.0,
        "USDT": 190.0, "XBX": 6608.0, "XIN": 5.0, "XLM": 0.005, "XRP": 0.1, "XTZ": 0.1, "ZEC": 0.004, "ZRX": 56.0
    }

    def find_best_sell_offer(self, crypto_curr, base_curr, quantity):
        orderbook_buy = self.get_orderbook(crypto_curr, base_curr, "buy")

        if orderbook_buy is None:
            return None

        self.__quick_sort_orderbook_by_rate(orderbook_buy)
        result = []

        if quantity < float(orderbook_buy[0]['ca']):
            map = {
                'Quantity': orderbook_buy[0]['ca'],
                'Rate': orderbook_buy[0]['ra']
            }
            return result.append(map)
        else:
            i = 0
            while quantity >= 0:
                map = {
                    'Quantity': orderbook_buy[i]['ca'],
                    'Rate': orderbook_buy[i]['ra']
                }
                result.append(map)
                quantity = quantity - float(orderbook_buy[i]['ca'])
                i = i + 1
        return result

    def get_markets_data(self):
        query = self.BASEURL + "ticker"
        response = super(BitBayAPI, self).query(query)
        if response.status_code == 200:
            return response.json().get('items')

    def get_market_names_list(self):
        all_markets = self.get_markets_data()
        all_names = []
        for market in all_markets:
            all_names.append(market)
        return all_names

    def get_orderbook(self, crypto_curr, base_curr, type):
        crypto_curr = crypto_curr.upper()
        base_curr = base_curr.upper()
        type = type.lower()
        if super(BitBayAPI, self).is_valid(crypto_curr, base_curr, type):
            query = self.BASEURL + "orderbook/" + crypto_curr + "-" + base_curr
            response = super(BitBayAPI, self).query(query)
            if response.status_code == 200:
                if type == "buy":
                    return response.json().get("buy")
                elif type == "sell":
                    return response.json().get("sell")
                else:
                    return response.json()

    def __quick_sort_orderbook_by_rate(self, unsorted):
        if len(unsorted) <= 1:
            return unsorted

        pivot = unsorted.pop()

        lower = []
        greater = []

        for item in unsorted:
            if float(item.get('ra')) < float(pivot.get('ra')):
                lower.append(item)
            else:
                greater.append(item)

        return self.__quick_sort_orderbook_by_rate(lower) + [pivot] + self.__quick_sort_orderbook_by_rate(greater)
